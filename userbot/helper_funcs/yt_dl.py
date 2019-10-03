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


from asyncio import get_event_loop
from concurrent.futures import Executor
import youtube_dl

from .. import LOGGER

loop = get_event_loop()


class YTdlLogger(object):
    """Logger used for YoutubeDL which logs to UserBot logger."""
    def debug(self, msg):
        """Logs debug messages with youtube-dl tag to UserBot logger."""
        LOGGER.debug("youtube-dl: " + msg)

    def warning(self, msg):
        """Logs warning messages with youtube-dl tag to UserBot logger."""
        LOGGER.warning("youtube-dl: " + msg)

    def error(self, msg):
        """Logs error messages with youtube-dl tag to UserBot logger."""
        LOGGER.error("youtube-dl: " + msg)

    def critical(self, msg):
        """Logs critical messages with youtube-dl tag to UserBot logger."""
        LOGGER.critical("youtube-dl: " + msg)


def hook(d):
    """YoutubeDL's hook which logs progress and erros to UserBot logger."""
    if d['status'] == 'downloading':
        filen = d['filename']
        prcnt = d['_percent_str']
        ttlbyt = d['_total_bytes_str']
        spdstr = d['_speed_str']
        etastr = d['_eta_str']

        finalStr = (
            "Downloading {}: {} of {} at {} ETA: {}".format(
                filen, prcnt, ttlbyt, spdstr, etastr
            )
        )
        LOGGER.info(finalStr)

    elif d['status'] == 'finished':
        filen = d['filename']
        ttlbyt = d['_total_bytes_str']
        elpstr = d['_elapsed_str']

        finalStr = (
            "Downloaded {}: 100% of {} in {}".format(
                filen, ttlbyt, elpstr
            )
        )
        LOGGER.warning(finalStr)

    elif d['status'] == 'error':
        finalStr = "Error:\n" + str(d)
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
    executor: Executor,
    params: dict,
    url: str,
    download: bool = False
) -> str:
    """Runs YoutubeDL's extract_info method without blocking the event loop.

    Args:
        executor (:obj:`Executor <concurrent.futures>`):
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
    ytdl = youtube_dl.YoutubeDL(params)

    def downloader(download):
        try:
            info_dict = ytdl.extract_info(url, download=download)
        except youtube_dl.utilsDownloadError as DE:
            return ("`" + str(DE) + "`")
        except youtube_dl.utilsContentTooShortError:
            return "`There download content was too short.`"
        except youtube_dl.utilsGeoRestrictedError:
            return (
                "`Video is not available from your geographic location due "
                "to geographic restrictions imposed by a website.`"
            )
        except youtube_dl.utilsMaxDownloadsReached:
            return "`Max-downloads limit has been reached.`"
        except youtube_dl.utilsPostProcessingError:
            return "`There was an error during post processing.`"
        except youtube_dl.utilsUnavailableVideoError:
            return "`Video is not available in the requested format.`"
        except youtube_dl.utilsXAttrMetadataError as XAME:
            return f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`"
        except youtube_dl.utilsExtractorError:
            return "`There was an error during info extraction.`"
        except Exception as e:
            eStr = str(type(e)) + ": " + str(e)
            return eStr

        if download is False:
            return info_dict
        else:
            title = info_dict.get(
                'title', info_dict.get('id', 'Unknown title')
            )
            return f"`Successfully downloaded {title}.`"

    fut = executor.submit(downloader, download)
    try:
        result = fut.result()
    except Exception as exc:
        LOGGER.exception(exc)
    finally:
        return result
