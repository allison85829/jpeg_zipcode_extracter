import os
import sys 
from uszipcode import SearchEngine, SimpleZipcode, Zipcode

search = SearchEngine()
def getzipcode(file_path):
    # return -1 if zipcode is not found or error 
    # return zipcode if found 
    img_f = open(file_path, 'rb')

    start_img = img_f.read(2)
    # check if the file is jpg 
    if (start_img == bytes.fromhex('ffd8')):
        print("This is a JPEG file")
    else:
        err_msg("This is not a JPEG file.", img_f)
        return -1 

    # check if the jpeg file use EXIF application marker 
    app_marker = img_f.read(2)
    if (app_marker != bytes.fromhex('FFE1')):
        err_msg("This jpeg file doesn't use EXIF application marker. "
            + "imggps doesn't support JFIF at the moment.", img_f)
        return -1

    img_f.read(8)
    exif_struct = img_f.read(2)
    # check if the jpeg is using little endian or big endian format 
    if (exif_struct == bytes.fromhex('4949')):
        print("little")
        return get_zipcode_little_endian(img_f)
    else:
        print("big")
        return get_zipcode_big_endian(img_f) 
    
    
def get_zipcode_big_endian(img_f):
    lat_ref = long_ref = "" 
    lat_degree = long_degree = ""  
    zipcode = -1  
    img_f.read(2)
    dir_offset = img_f.read(4)

    num_dir_entry = img_f.read(2)
    num_dir_entry = int(num_dir_entry.hex(),16)

    # this the start of the TIFF header 
    # all the offset is relative to this position. 
    start = 12 
    dir_offset = int(dir_offset.hex(), 16)
    # offset to the first IFD as integer
    img_f.seek(start + dir_offset, 0)

    img_f.read(2)
    for i in range(num_dir_entry):
        tag_type = img_f.read(2)

        cnt = 0
        if (tag_type == bytes.fromhex('8825')):
            img_f.read(6)
            # read the address to the start of GPS info IFD 
            gps_info_ptr = img_f.read(4)
            gps_info_ptr = int(gps_info_ptr.hex(), 16)
            img_f.seek(start + gps_info_ptr, 0)

            # read the number of entry of the GPS IFD
            gps_num_entry = img_f.read(2)
            gps_num_entry = int(gps_num_entry.hex(), 16)
            
 
            for j in range(gps_num_entry):
                # reading the file tag ID for entry in the GPS IFD 
                gps_tag_type = img_f.read(2)

                if (gps_tag_type == bytes.fromhex('0001')):
                    # longitude reference N, S
                    lat_ref = get_coord_ref(img_f)
                    cnt += 1
                elif (gps_tag_type == bytes.fromhex('0003')):
                    # longitude reference E, W
                    long_ref = get_coord_ref(img_f)
                    cnt += 1
                elif (gps_tag_type == bytes.fromhex('0002')):
                    # give latitude coordinate
                    lat_degree = get_coord_component(img_f, start, 0)
                    cnt += 1
                elif (gps_tag_type == bytes.fromhex('0004')):
                    # give longitude coordinate
                    long_degree = get_coord_component(img_f, start, 0)
                    cnt += 1
                    # break
                else:
                    img_f.read(10)
                if (cnt==4):
                    break

            if (check_no_gps_info(lat_degree, long_degree) == 0):
                err_msg("Cannot found GPS information", img_f)
                return -1 
            res = gps_coord_to_zipcode(lat_ref, long_ref, lat_degree, long_degree, search)
            if (len(res) == 0):
                err_msg("This location is outside of the US.", img_f)
                return -1
            zipcode = res[0].zipcode
            # stop looking if found the GPS information
            break
        else:
            img_f.read(10)
    img_f.close()
    return int(zipcode) 


def get_zipcode_little_endian(img_f):
    lat_ref = long_ref = "" 
    lat_degree = long_degree = "" 
    search = SearchEngine()
    zipcode = -1 
    img_f.read(2)
    dir_offset = img_f.read(4)

    num_dir_entry = img_f.read(2)
    num_dir_entry = little_to_big_endian(num_dir_entry, 2)

    # this the start of the TIFF header 
    # all the offset is relative to this position. 
    start = 12 
    dir_offset = little_to_big_endian(dir_offset, 4) # int 
    # offset to the first IFD as integer
    img_f.seek(start + dir_offset, 0)

    img_f.read(2)
    for i in range(num_dir_entry):
        tag_type = img_f.read(2)
        tag_type = little_to_big_endian(tag_type, 2)

        cnt = 0
        if (tag_type == int('8825', 16)):
            img_f.read(6)
            # read the address to the start of GPS info IFD 
            gps_info_ptr = img_f.read(4)
            gps_info_ptr = little_to_big_endian(gps_info_ptr, 4)
            img_f.seek(start + gps_info_ptr, 0)

            # read the number of entry of the GPS IFD
            gps_num_entry = img_f.read(2)
            gps_num_entry = little_to_big_endian(gps_num_entry, 2)
            for j in range(gps_num_entry):
                # reading the file tag ID for entry in the GPS IFD 
                gps_tag_type = img_f.read(2)
                gps_tag_type = little_to_big_endian(gps_tag_type, 2)

                # check the tag for the type of gps information 
                if (gps_tag_type == int('0001', 16)):
                    # longitude reference N, S
                    lat_ref = get_coord_ref(img_f)
                    cnt += 1
                elif (gps_tag_type == int('0003', 16)):
                    # longitude reference E, W
                    long_ref = get_coord_ref(img_f)
                    cnt += 1
                elif (gps_tag_type == int('0002', 16)):
                    # give latitude coordinate
                    lat_degree = get_coord_component(img_f, start, 1)
                    cnt += 1
                elif (gps_tag_type == int('0004', 16)):
                    # give longitude coordinate
                    long_degree = get_coord_component(img_f, start, 1)
                    cnt += 1
                else:
                    img_f.read(10)
                if (cnt==4):
                    break
            
            if (check_no_gps_info(lat_degree, long_degree) == 0):
                err_msg("Cannot found GPS information", img_f)
                return -1 
            res = gps_coord_to_zipcode(lat_ref, long_ref, lat_degree, long_degree, search)
            if (len(res) == 0):
                err_msg("This location is outside of the US.", img_f)
                return -1
            zipcode = res[0].zipcode
            # stop looking if found the GPS information
            break
        else:
            img_f.read(10)
    img_f.close()
    return int(zipcode) 

# check if no latitude and longitude has been found
def check_no_gps_info(lat, long):
    if (lat == ""  or long == ""):
        return 0 
    else:
        return 1

def gps_coord_to_zipcode(lat_ref, long_ref, lat, long, search):
    # after getting all the GPS coordinates --> get the zipcode             
    if (lat_ref == bytes.fromhex('53')):
        # ASCII code for 'S' is 53 
        lat = -1.0*lat
    
    if (long_ref == bytes.fromhex('57')):
        # ASCII code for 'W' is 57
        long = -1.0*long
    return search.by_coordinates(lat, long, radius=5)


def get_coord_component(f, start, data_format):
    f.read(6)
    comp_ptr = f.read(4)
    if data_format == 1: # 1: little endian, 0: big endian
        comp_ptr = little_to_big_endian(comp_ptr, 4)
    else:
        comp_ptr = int(comp_ptr.hex(), 16)
    # pointer to the next entry in the GPS IFD 
    # which also is the current location 
    cur_ptr = f.tell()
    # get pointer to the array of coordinate info 
    # using the offset which is comp_tr 
    f.seek(start + comp_ptr, 0)

    if data_format == 1:
        degree, minute, second = get_coordinate_little(f)
    else:
        degree, minute, second = get_coordinate(f)
    coord_comp = get_decimal_degree(degree, minute, second)
    f.seek(cur_ptr, 0)
    return coord_comp


def get_coord_ref(f):
    # get the longitude and latitue reference N,E,S,W
    f.read(6)
    # longitude and latitude coordinate reference is an ascii character 
    # which is 1 byte  
    coord_ref =  f.read(1)
    f.read(3)
    return coord_ref

def err_msg(msg, f):
    # take in a msg string and the image file object 
    print(msg)
    f.close()
        
def get_coordinate(f):
    # take in the image file object 
    # and return the gps coordinate in degree, minute and second as integers
    degree_numerator = int(f.read(4).hex(), 16)
    degree_denominator = int(f.read(4).hex(), 16)
    degree = (degree_numerator*1.0)/degree_denominator
    minute_numerator = int(f.read(4).hex(), 16)
    minute_denominator = int(f.read(4).hex(), 16)
    minute = (minute_numerator*1.0)/minute_denominator
    second_numerator = int(f.read(4).hex(), 16)
    second_denominator = int(f.read(4).hex(), 16)
    second = (second_numerator*1.0)/second_denominator
    return degree, minute, second 

def get_coordinate_little(f):
    # the same as get_coordinate(f) but for little endian format
    degree_numerator = little_to_big_endian(f.read(4), 4)
    degree_denominator = little_to_big_endian(f.read(4), 4)
    degree = (degree_numerator*1.0)/degree_denominator
    minute_numerator = little_to_big_endian(f.read(4), 4)
    minute_denominator = little_to_big_endian(f.read(4), 4)
    minute = (minute_numerator*1.0)/minute_denominator
    second_numerator = little_to_big_endian(f.read(4), 4)
    second_denominator = little_to_big_endian(f.read(4), 4)
    second = (second_numerator*1.0)/second_denominator
    return degree, minute, second 

def get_decimal_degree(degree, minutes, seconds):
    # convert gps coordinate into decimal degree 
    return degree + minutes/60.0 + seconds/3600.0

def little_to_big_endian(num, num_bytes):
    # Convert the bytes from little edian to big endian 
    # num_bytes specify how many bytes in the number that need to be convert
    # In this program, only read 2 bytes or 4 bytes for needed information
    n = int(num.hex(), 16)
    if (num_bytes == 2):
        b1 = (n & 0x0000ff00) >> 8
        b2 = (n & 0x000000ff) << 8
        n = b1 | b2
    elif (num_bytes == 4):
        b1 = (n & 0xff000000) >> 24
        b2 = (n & 0x00ff0000) >> 8
        b3 = (n & 0x0000ff00) << 16
        b4 = (n & 0x000000ff) << 16
        n = b1 | b2 | b3 | b4
    return n

if __name__ == "__main__":
    print(len(sys.argv))
    num_args = len(sys.argv)
    dir_path = os.getcwd()

    for i in range(1, num_args):
        print(str(i) + ". " + sys.argv[i])
        file_path = dir_path + "/" + sys.argv[i]
        zipcode = getzipcode(file_path)
        if (zipcode != -1):
            print("     zipcode: " + str(zipcode))
        else:
            print("     No zipcode information founded.")
        print("====================================")
