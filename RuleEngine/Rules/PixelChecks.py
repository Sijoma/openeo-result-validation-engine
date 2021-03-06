import logging
import os

import cv2

from RuleEngine.Algorithms.compare_resolution import compare_resolution
from RuleEngine.Algorithms.image_funcs import image_similarity_measures
from RuleEngine.Rules.Rule import Rule


class PixelChecks(Rule):
    def __init__(self, parameters):
        self._name_of_rule = 'pixel-checks'
        super(PixelChecks, self).__init__(parameters)

    def check_rule(self, image_path_a, image_path_b, combination):
        """ Has two image paths as input, the threshold comes from the instantiation of the rule"""
        logger = logging.getLogger(self.get_name_of_rule())

        image_a = self.read_image(image_path_a)
        image_b = self.read_image(image_path_b)

        try:
            if image_a and image_b:
                print('Images read')
            else:
                return {'passed': False,
                        'message': 'Reading image'}
        except ValueError as e:
            """ Workaround, sometimes the image cannot be loaded and thus we cannot check with .all()"""


        resize_factor = self._parameters.get('resize-factor')
        logger.info('Using resize factor of ' + str(resize_factor))
        if resize_factor:
            image_a = cv2.resize(image_a, None, fx=resize_factor, fy=resize_factor)
            image_b = cv2.resize(image_b, None, fx=resize_factor, fy=resize_factor)

        result = {'passed': False}

        if self._parameters.get('image-similarity-measures', 0) is not 0:
            result['compare_resolution'] = compare_resolution(image_a, image_b)
            logger.info('Checking resolution')
            resolution_allowed_divergence = self._parameters.get('resolution-allow-divergence')

            result_resolution_check = [
                1 - resolution_allowed_divergence < resolution_factor < 1 + resolution_allowed_divergence
                for resolution_factor in result['compare_resolution']['resolution_factors']]

            if False in result_resolution_check:
                result['compare_resolution']['passed'] = str(False)
            else:
                result['compare_resolution']['passed'] = str(True)

            logger.info('Executing Image Similarity measures')
            try:
                result['image-similarity-measures'], difference_image = \
                    image_similarity_measures(image_a, image_b)
                # If there is a difference image and there are differences => store the file
                if difference_image is not None and result['image-similarity-measures']['compare_ssim'] != 1.0:
                    file_save_path = self.create_file_path(combination, 'SSIM_', '.png')
                    cv2.imwrite(file_save_path, difference_image)
                    result['differenceImage_Path'] = os.path.split(file_save_path)[1]

                ism_passed = result['image-similarity-measures']['compare_ssim'] >= self._parameters.get('image-similarity-measures')

                result['image-similarity-measures']['passed'] = str(ism_passed)
            except ValueError as e:
                result['image-similarity-measures'] = {
                    'passed': 'False',
                    'error': str(e)}

            if result['compare_resolution']['passed'] == 'True' \
                    and result['image-similarity-measures']['passed'] == 'True':
                result['passed'] = 'True'
            else:
                result['passed'] = 'False'



        return result

