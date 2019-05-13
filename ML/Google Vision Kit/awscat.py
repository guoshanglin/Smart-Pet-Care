#!/usr/bin/env python3

# from object_detection.py`
import argparse
from PIL import Image, ImageDraw
from aiy.vision.inference import ImageInference
from aiy.vision.models import object_detection
from picamera import PiCamera

import time
import boto3


# connect to AWS S3
s3 = boto3.resource('s3',
    aws_access_key_id="",
    aws_secret_access_key=""
)


def crop_center(image):
    width, height = image.size
    size = min(width, height)
    x, y = (width - size) / 2, (height - size) / 2
    return image.crop((x, y, x + size, y + size)), (x, y)


def recognize(inputfile, outputfile, outputfile_detected):
    threshold = 0.3
    if inputfile == None:
        # camera capture
        with PiCamera() as camera:
            camera.resolution = (1640, 922)  # Full Frame, 16:9 (Camera v2)
            camera.start_preview()

            while True:
                camera.capture(outputfile)
                image = Image.open(outputfile)
                image_center, offset = crop_center(image)
                draw = ImageDraw.Draw(image)

                is_pet = False
                with ImageInference(object_detection.model()) as inference:
                    result = inference.run(image_center)
                    objects = object_detection.get_objects(result, threshold, offset)
                    for i, obj in enumerate(objects):
                        print('Object #%d kind%d: %s' % (i, obj.kind, obj))
                        if obj.kind>1:
                            is_pet = True
                        x0, y0, width, height = obj.bounding_box
                        x1 = x0+width
                        y1 = y0+height
                        d = 5
                        draw.rectangle((x0, y0, x0+d, y1), fill='red', outline='red')
                        draw.rectangle((x0, y0, x1, y0+d), fill='red', outline='red')
                        draw.rectangle((x0, y1-d, x1, y1), fill='red', outline='red')
                        draw.rectangle((x1-d, y0, x1, y1), fill='red', outline='red')
                image.save(outputfile)
                time.sleep(1)
                # if pet deteced, update pet image in AWS S3
                if is_pet:
                    s3.meta.client.upload_file(outputfile, 'iot6765project', 
                        'webapp/'+outputfile_detected, ExtraArgs={'ACL':'public-read'})
                else:
                    print('No Pet Detected')
                # update result image in AWS S3
                s3.meta.client.upload_file(outputfile, 'iot6765project', 
                    'webapp/'+outputfile, ExtraArgs={'ACL':'public-read'})
            camera.stop_preview()


recognize(None, "result.jpg", "result_cat.jpg")


