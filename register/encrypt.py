#用于加密和解密
import base64

def main():
    #转成bytes string
    bytesString = copyright.encode(encoding="utf-8")
    print(bytesString)

    #base64 编码
    encodestr = base64.b64encode(bytesString)
    print(encodestr)
    print(encodestr.decode())

    #解码
    decodestr = base64.b64decode(encodestr)
    print(decodestr.decode())

if __name__ == '__main__':
    main()