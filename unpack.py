#!python
import os,sys
from xml.etree import ElementTree
from PIL import Image
import codecs
import locale
import string

def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'integer':
                d[item.text] = locale.atoi(tree[index + 1].text)
            elif tree[index + 1].tag == 'real':
                d[item.text] = locale.atoi(tree[index + 1].text)
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d

def gen_png_from_plist_v0(plist_filename, png_filename,file_path):
    big_image = Image.open(png_filename)
    to_list = lambda x: x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():
        width = v['width']
        height = v['height']

        rectlist=[v['x'],v['y']]
        print('width=',width)
        print('height=',height)
        box=(
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0]) + width,
            int(rectlist[1]) + height,
            )
        sizelist = [ v['originalWidth'],v['originalHeight']]
        print ('sizelist=',sizelist)
        rect_on_big = big_image.crop(box)

        result_image = Image.new('RGBA', sizelist, (0,0,0,0))
        result_box=(
            int(( sizelist[0] - width )/2),
            int(( sizelist[1] - height )/2),
            int(( sizelist[0] + width )/2),
            int(( sizelist[1] + height )/2)
            )
        print('result_box=',result_box)
        result_image.paste(rect_on_big, result_box, mask=0)

        if not os.path.isdir(file_path):
            os.mkdir(file_path)

        index = k.find('/', 0);
        parentdir=file_path + '/' + k[:index]
        print (parentdir)
        if (index!=-1):
            ##create dir
            if not os.path.isdir(parentdir):
                os.mkdir(parentdir)

        outfile = (file_path+'/' + k).replace('gift_', '')

        print (outfile, "generated")
        result_image.save(outfile)

def gen_png_from_plist_v2(plist_dict, png_filename,file_path):
    big_image = Image.open(png_filename)
    all_text=open(plist_filename, encoding='utf_8_sig').read()
    to_list = lambda x: x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():
        rectlist = to_list(v['frame'])
        width = int( rectlist[3] if v['rotated'] else rectlist[2] )
        height = int( rectlist[2] if v['rotated'] else rectlist[3] )
        print('width=',width)
        print('height=',height)
        box=(
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0]) + width,
            int(rectlist[1]) + height,
            )
        sizelist = [ int(x) for x in to_list(v['sourceSize'])]
        print ('sizelist=',sizelist)
        rect_on_big = big_image.crop(box)

        if v['rotated']:
            rect_on_big = rect_on_big.rotate(90)

        result_image = Image.new('RGBA', sizelist, (0,0,0,0))
        if v['rotated']:
            result_box=(
                int(( sizelist[0] - height )/2),
                int(( sizelist[1] - width )/2),
                int(( sizelist[0] + height )/2),
                int(( sizelist[1] + width )/2)
                )
        else:
            result_box=(
                int(( sizelist[0] - width )/2),
                int(( sizelist[1] - height )/2),
                int(( sizelist[0] + width )/2),
                int(( sizelist[1] + height )/2)
                )
        print('result_box=',result_box)
        result_image.paste(rect_on_big, result_box, mask=0)

        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        outfile = (file_path+'/' + k).replace('gift_', '')
        print (outfile, "generated")
        result_image.save(outfile)

def check_plist_ver(plist_dict):
    for k,v in plist_dict['metadata'].items():
##        print(k)
##        print(v)
        if (k == 'format'):
            return v
    return -1

def get_plist_imagefilename(plist_dict):
    for k,v in plist_dict['metadata'].items():
        if (k == 'realTextureFileName'):
            return v
    return ''

if __name__ == '__main__':
    filename = sys.argv[1]
    plist_filename = filename + '.plist'

    if (os.path.exists(plist_filename)):
        file_path = plist_filename.replace('.plist', '')
        all_text=open(plist_filename, encoding='utf_8_sig').read()
        root = ElementTree.fromstring(all_text)
        plist_dict = tree_to_dict(root[0])
        ver=check_plist_ver(plist_dict)

        imagefilename=get_plist_imagefilename(plist_dict)

        index = imagefilename.find('pvr.ccz', 0);
        if (index!=-1):
            imagefilename=filename + '.png'

        if (os.path.exists(imagefilename)):
            if (ver == 0):
                print ("the plist file format is ver 0")
                gen_png_from_plist_v0(plist_dict,imagefilename,file_path)
            elif (ver == 2):
                print ("the plist file format is ver 2")
                gen_png_from_plist_v2(plist_dict,imagefilename,file_path)
            else:
                print ("the plist file format is ver ",ver,",that is not supported.")
        else:
            print ("make sure ", imagefilename, " file is existed")
    else:
         print ("make sure ",filename,".plist file is existed")
##    if (os.path.exists(plist_filename) and os.path.exists(png_filename)):
##        gen_png_from_plist( plist_filename, png_filename )
##    else:
##        print ("make sure you have boith plist and png files in the same directory")