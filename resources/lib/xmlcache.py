import os, requests, shutil
import time
import gzip, lzma

def arrange_path(url, path):

    try:
        if os.path.exists(path):
            if os.path.getmtime(path) + 86400 > time.time():
                return True, path
            else:
                os.remove(path)

        if "http://" in url or "https://" in url:
            if url.endswith(".gz"):
                with open(path, "wb") as f:
                    t = requests.get(url).content
                    try:
                        f.write(gzip.decompress(t))
                    except gzip.BadGzipFile:
                        f.write(t)
                    except Exception as e:
                        return False, f"Failed to decompress the XMLTV file: {str(e)}"
            elif url.endswith(".xz"):
                with open(path, "wb") as f:
                    f.write(lzma.decompress(requests.get(url).content))
            elif url.endswith(".xml"):
                with open(path, "wb") as f:
                    f.write(requests.get(url).content)
        else:
            if url.endswith(".gz"):
                with open(path, "wb") as f:
                    f.write(gzip.decompress(open(url.replace("file://", ""), "rb").read()))
            elif url.endswith(".xz"):
                with open(path, "wb") as f:
                    f.write(lzma.decompress(open(url.replace("file://", ""), "rb").read()))
            elif url.endswith(".xml"):
                shutil.copyfile(url.replace("file://", ""), path)
            
        with open(path, "rb") as f:
            for i in f:
                if i.startswith(b"<?xml"):
                    return True, path

        os.remove(path)
        return False, "The XMLTV file type could not be verified."
    except Exception as e:
        try:
            os.remove(path)
        except:
            pass
        return False, str(e)
