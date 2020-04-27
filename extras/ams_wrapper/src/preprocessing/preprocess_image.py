#
# Copyright (c) 2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from typing import Tuple

import tensorflow as tf
import numpy as np


class ImageDecodeError(ValueError):
    pass


class ImageResizeError(ValueError):
    pass


class ImagePreprocessError(ValueError):
    pass


def preprocess_binary_image(image: bytes, channels: int = None,
                            target_size: Tuple[int, int] = None,
                            channels_first=True,
                            dtype=tf.dtypes.uint8, scale: float = None,
                            standardization=False,
                            reverse_input_channels=False) -> np.ndarray:
    """
    Preprocess binary image in PNG, JPG or BMP format, producing numpy array as a result.

    :param image: Image bytes
    :param channels: Number of image's channels
    :param target_size: A tuple of desired height and width
    :param channels_first: If set to True, image array will be in NCHW format,
     NHWC format will be used otherwise
    :param dtype: Data type that will be used for decoding
    :param scale: If passed, decoded image array will be multiplied by this value
    :param standardization: If set to true, image array values will be standarized
    to have mean 0 and standard deviation of 1
    :param reverse_input_channels: If set to True, image channels will be reversed
    from RGB to BGR format
    :raises ImageDecodeError(ValueError): if image cannot be decoded
    :raises ImageResizeError(ValueError): if image cannot be resized
    :raises ImagePreprocessError(ValueError): if image cannot be preprocessed
    :returns: Preprocessed image as numpy array
    """

    try:
        decoded_image = tf.io.decode_image(image, channels=channels, dtype=dtype)
    except Exception as e:
        raise ImageDecodeError('Provided image is invalid, unable to decode.') from e

    if target_size:
        try:
            height, width = target_size
            decoded_image = tf.image.resize_with_crop_or_pad(decoded_image, height, width)
        except Exception as e:
            raise ImageResizeError('Failed to resize provided binary image from: {} '
                                   'to: {}.'.format(tf.shape(decoded_image), target_size)) from e

    try:
        image_array = decoded_image.numpy()
        if standardization:
            decoded_image = tf.image.per_image_standardization(decoded_image)
        if reverse_input_channels:
            image_array = image_array[..., ::-1]
        if channels_first:
            image_array = np.transpose(image_array, [2, 0, 1])
        if scale:
            image_array = image_array * scale
    except Exception as e:
        raise ImagePreprocessError('Failed to preprocess binary image, '
                                   'check if provided parameters are correct.') from e

    return image_array



if __name__ == "__main__":
    img_path = '<path to the image>'
    with open(img_path, mode='rb') as img_file:
        binary_image = img_file.read()

    preprocessed_image = preprocess_binary_image(binary_image, channels_first=False)
    print(preprocessed_image.shape)

    # Keep in mind that matplotlib will not be able to display image in NCHW format
    try:
        import matplotlib.pyplot as plt
        plt.imshow(preprocessed_image)
        plt.show()
    except ImportError:
        print('Please install matplotlib if you want to inspect preprocessed image.')
