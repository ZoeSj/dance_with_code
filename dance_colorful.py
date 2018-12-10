#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from concurrent.futures import wait, ProcessPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageDraw

__author__ = 'brick'
__date__ = '2018-11-22 17:49'
__project__ = 'test'
__description__ = ''


def image2ascii(n, srd_img_file_dir, dst_img_dir, scale=1, sample_step=7):
    # read image
    old_img = Image.open(os.path.join(srd_img_file_dir, n))

    pix = old_img.load()
    width = old_img.size[0]
    height = old_img.size[1]
    # print("width:%d, height:%d" % (width, height))

    # create new image
    canvas = np.ndarray((height * scale, width * scale, 3), np.uint8)
    canvas[:, :, :] = 255
    new_image = Image.fromarray(canvas)
    draw = ImageDraw.Draw(new_image)

    char_table = list('anchnet')

    # draw
    pix_count = 0
    table_len = len(char_table)
    for y in range(height):
        for x in range(width):
            if x % sample_step == 0 and y % sample_step == 0:
                # print('r: {0}, g: {1}, b: {2}'.format(r, g, b))
                draw.text((x * scale, y * scale), char_table[pix_count % table_len], pix[x, y])  # colorful
                pix_count += 1

    # save
    dst = os.path.join(dst_img_dir, n)
    new_image.save(dst)

    # new_image.show()


def video2txtimage(video_file, videoimage_dir, ascii_image_dir):
    if not os.path.exists(video_file):
        raise Exception("No such file or directory '{}'".format(video_file))
    if os.path.isdir(video_file):
        raise Exception("Is a directory '{}'".format(video_file))

    video = cv2.VideoCapture(video_file)
    futures = []
    if video.isOpened():
        total_num = video.get(7)
        with ProcessPoolExecutor() as executor:
            for num in range(int(total_num) - 1):
                r, frame = video.read()
                cv2.imwrite(videoimage_dir + str(num) + '.jpg', frame)
                print('The %d frame images generated' % num)
                future = executor.submit(image2ascii, *[str(num) + '.jpg', videoimage_dir, ascii_image_dir])
                futures.append(future)
                # image2ascii(str(num) + '.jpg', videoimage_dir, ascii_image_dir)
        wait(futures)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        return fps
    else:
        print("Read video failed")


def image2video(image_dir, out_file, fps):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    images = os.listdir(image_dir)
    im = Image.open(image_dir + '/' + images[0])
    new_video = cv2.VideoWriter(out_file + '.avi', fourcc, fps, im.size)
    os.chdir(image_dir)
    for image in range(1, len(images) + 1):
        frame = cv2.imread(str(image) + '.jpg')
        new_video.write(frame)
    print('Video compound finished')
    new_video.release()


def del_files(*paths):
    for path in paths:
        ls = os.listdir(path)
        for i in ls:
            p = os.path.join(path, i)
            if os.path.isdir(p):
                del_files(p)
            else:
                os.remove(p)


def check_dir(*paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == '__main__':
    start_time = int(time.time())
    video_src = '/usr/local/var/www/python/dance/test/tmp/input.mp4'  # source video
    ascii_image_dir = '/usr/local/var/www/python/dance/tmp/ascii_images/'  # tmp
    videoimage_dir = '/usr/local/var/www/python/dance/tmp/video_images/'  # tmp
    video_result = '/usr/local/var/www/python/dance/tmp/test'  # destination video

    check_dir(ascii_image_dir, videoimage_dir)
    del_files(ascii_image_dir, videoimage_dir)
    #
    fps = video2txtimage(video_src, videoimage_dir, ascii_image_dir)
    image2video(ascii_image_dir, video_result, fps)
    # image2ascii('1.jpg', videoimage_dir, ascii_image_dir)
    end_time = int(time.time())
    print("used time : %d second." % (int(time.time()) - start_time))
