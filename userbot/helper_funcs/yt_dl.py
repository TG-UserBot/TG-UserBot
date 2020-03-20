# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.


import concurrent
import datetime
import functools
import os
import pathlib
import re
import time
import youtube_dl

from .. import LOGGER


downloads = {}
audio = re.compile(r'\[ffmpeg\] Destination\: (.+)')
video = re.compile(
    r'\[ffmpeg\] Converting video from \w+ to \w+, Destination: (.+)'
)
merger = re.compile(r'\[ffmpeg\] Merging formats into "(.+)"')


class YTdlLogger(object):
    """Logger used for YoutubeDL which logs to UserBot logger."""
    def debug(self, msg: str) -> None:
        """Logs debug messages with youtube-dl tag to UserBot logger."""
        LOGGER.debug("youtube-dl: " + msg)
        f = None
        if "[ffmpeg]" in msg:
            if audio.search(msg):
                f = audio.match(msg).group(1)
            if video.search(msg):
                f = video.match(msg).group(1)
            if merger.search(msg):
                f = merger.match(msg).group(1)
            if f:
                downloads.update(**{f.split('.')[0]: f})

    def warning(self, msg: str) -> None:
        """Logs warning messages with youtube-dl tag to UserBot logger."""
        LOGGER.warning("youtube-dl: " + msg)

    def error(self, msg: str) -> None:
        """Logs error messages with youtube-dl tag to UserBot logger."""
        LOGGER.error("youtube-dl: " + msg)

    def critical(self, msg: str) -> None:
        """Logs critical messages with youtube-dl tag to UserBot logger."""
        LOGGER.critical("youtube-dl: " + msg)


class ProgressHook():
    """Custom hook with the event stored for YTDL."""
    def __init__(self, event):
        self.event = event
        self.last_edit = None
        self.tasks = []

    def callback(self, task):
        """Cancel pending tasks else skip them if completed."""
        if task.cancelled():
            return
        else:
            new = task.result().date
            if new > self.last_edit:
                self.last_edit = new

    def edit(self, *args, **kwargs):
        """Create a Task of the progress edit."""
        task = self.event.client.loop.create_task(
            self.event.answer(*args, **kwargs)
        )
        task.add_done_callback(self.callback)
        self.tasks.append(task)
        return task

    def hook(self, d: dict) -> None:
        """YoutubeDL's hook which logs progress and errors to UserBot logger."""
        if not self.last_edit:
            self.last_edit = datetime.datetime.now(datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        if d['status'] == 'downloading':
            filen = d.get('filename', 'Unknown filename')
            prcnt = d.get('_percent_str', None)
            ttlbyt = d.get('_total_bytes_str', None)
            spdstr = d.get('_speed_str', None)
            etastr = d.get('_eta_str', None)

            if not prcnt or not ttlbyt or not spdstr or not etastr:
                return

            finalStr = (
                "Downloading {}: {} of {} at {} ETA: {}".format(
                    filen, prcnt, ttlbyt, spdstr, etastr
                )
            )
            LOGGER.debug(finalStr)
            if (
                not self.last_edit or
                (now - self.last_edit).total_seconds() > 5
            ):
                filen = re.sub(r'YT_DL\\(.+)_\d+\.', r'\1.', filen)
                self.edit(
                    f"`Downloading {filen} at {spdstr}.`\n"
                    f"__Progress: {prcnt} of {ttlbyt}__\n"
                    f"__ETA: {etastr}__"
                )

        elif d['status'] == 'finished':
            filen = d.get('filename', 'Unknown filename')
            filen1 = re.sub(r'YT_DL\\(.+)_\d+\.', r'\1.', filen)
            ttlbyt = d.get('_total_bytes_str', None)
            elpstr = d.get('_elapsed_str', None)

            if not ttlbyt or not elpstr:
                return

            finalStr = f"Downloaded {filen}: 100% of {ttlbyt} in {elpstr}"
            LOGGER.warning(finalStr)
            self.event.client.loop.create_task(
                self.event.answer(
                    f"`Successfully downloaded {filen1} in {elpstr}!`"
                )
            )
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            self.tasks.clear()

        elif d['status'] == 'error':
            finalStr = "Error: " + str(d)
            LOGGER.error(finalStr)


async def list_formats(info_dict: dict) -> str:
    """YoutubeDL's list_formats method but without format notes.

    Args:
        info_dict (``dict``):
            Dictionary which is returned by YoutubeDL's extract_info method.

    Returns:
        ``str``:
            All available formats in order as a string instead of stdout.
    """
    formats = info_dict.get('formats', [info_dict])
    table = [
        [f['format_id'], f['ext'], youtube_dl.YoutubeDL.format_resolution(f)]
        for f in formats
        if f.get('preference') is None or f['preference'] >= -1000]
    if len(formats) > 1:
        table[-1][-1] += (' ' if table[-1][-1] else '') + '(best)'

    header_line = ['format code', 'extension', 'resolution']
    fmtStr = (
        '`Available formats for %s:`\n`%s`' %
        (info_dict['title'], youtube_dl.render_table(header_line, table))
    )
    return fmtStr


async def extract_info(
    loop,
    executor: concurrent.futures.Executor,
    ydl_opts: dict,
    url: str,
    download: bool = False
) -> str:
    """Runs YoutubeDL's extract_info method without blocking the event loop.

    Args:
        executor (:obj:`concurrent.futures.Executor <concurrent.futures>`):
            Either ``ThreadPoolExecutor`` or ``ProcessPoolExecutor``.
        params (``dict``):
            Parameters/Keyword arguments to use for YoutubeDL.
        url (``str``):
            The url which you want to use for extracting info.
        download (``bool``, optional):
            If you want to download the video. Defaults to False.

    Returns:
        ``str``:
            Successfull string or info_dict on success or an exception's
            string if any occur.
    """
    ydl_opts['outtmpl'] = ydl_opts['outtmpl'].format(time=time.time_ns())
    ytdl = youtube_dl.YoutubeDL(ydl_opts)

    def downloader(url, download):
        eStr = None
        try:
            info_dict = ytdl.extract_info(url, download=download)
        except youtube_dl.utils.DownloadError as DE:
            eStr = f"`{DE}`"
        except youtube_dl.utils.ContentTooShortError:
            eStr = "`There download content was too short.`"
        except youtube_dl.utils.GeoRestrictedError:
            eStr = (
                "`Video is not available from your geographic location due "
                "to geographic restrictions imposed by a website.`"
            )
        except youtube_dl.utils.MaxDownloadsReached:
            eStr = "`Max-downloads limit has been reached.`"
        except youtube_dl.utils.PostProcessingError:
            eStr = "`There was an error during post processing.`"
        except youtube_dl.utils.UnavailableVideoError:
            eStr = "`Video is not available in the requested format.`"
        except youtube_dl.utils.XAttrMetadataError as XAME:
            eStr = f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`"
        except youtube_dl.utils.ExtractorError:
            eStr = "`There was an error during info extraction.`"
        except Exception as e:
            eStr = f"`{type(e)}: {e}`"
            raise e
        if eStr:
            return eStr

        if download:
            filen = ytdl.prepare_filename(info_dict)
            opath = downloads.pop(filen.split('.')[0], filen)
            npath = re.sub(r'_\d+(\.\w+)$', r'\1', opath)
            thumb = pathlib.Path(re.sub(r'\.\w+$', r'.jpg', opath))

            old_f = pathlib.Path(npath)
            new_f = pathlib.Path(opath)
            if old_f.exists():
                if old_f.samefile(new_f):
                    os.remove(str(new_f.absolute()))
                else:
                    newname = str(old_f.stem) + '_OLD'
                    old_f.replace(
                        old_f.with_name(newname).with_suffix(old_f.suffix)
                    )
            path = new_f.parent.parent / npath
            new_f.rename(new_f.parent.parent / npath)
            thumb = str(thumb.absolute()) if thumb.exists() else None
            return path.absolute(), thumb, info_dict
        else:
            return info_dict

    # Future blocks the running event loop
    # fut = executor.submit(downloader, url, download)
    # result = fut.result()
    return await loop.run_in_executor(
        concurrent.futures.ThreadPoolExecutor(),
        functools.partial(downloader, url, download)
    )
