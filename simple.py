# -*- Mode: Python -*- vi:si:et:sw=4:sts=4:ts=4:syntax=python
#
# Copyright (c) 2017,Thibault Saunier <thibault.saunier@os.samsung.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.

"""
Simple validate testsuite built for v4l2 elements (for the exynos platform)
"""
import os
import subprocess


TEST_MANAGER = "validate"
CDIR = os.path.abspath(os.path.dirname(__file__))
EXPECTED_ISSUES = {r'validate.launch_pipeline.v4l2.convert.*.to.y42b.play_15s':
                   [
                       {'level': 'critical',
                        'summary': 'Compared images where not similar enough'
                        }
                   ]}


def get_element_name(elformat, _filter=None):
    for i in range(10):
        try:
            ename = elformat % i
            out = subprocess.check_output(["gst-inspect-1.0", ename], stderr=subprocess.STDOUT).decode()
            if not _filter or _filter in out:
                return ename
        except subprocess.CalledProcessError:
            continue


def add_format_conversion_tests(pipelines_descriptions):
    converter = get_element_name('v4l2video%dconvert')
    if not converter:
        print("Could not find any v4l2 converter!")
        return False

    formats = ["BGRx", "YUY2", "UYVY", "YVYU", "Y42B", "NV16", "NV61", "YV12",
                              "NV12", "NV21", "I420"]
    config = open(os.path.join(CDIR, 'check_frames.config'), mode='w')
    config.write('ssim, element-classification="Filter/Converter/Video/Scaler",'
                 ' reference-images-dir=%s/medias/refs/white/\n' % CDIR)
    config.flush()
    for inf in formats:
        for outf in formats:
            pipelines_descriptions.append(('v4l2.convert.%s.to.%s' % (inf.lower(), outf.lower()),
                                           "videotestsrc pattern=white num-buffers=1 ! "
                                           "video/x-raw,format=%s ! %s ! video/x-raw,format=%s ! fakesink" % (
                                               inf, converter, outf),
                                               {'extra_env_vars': {'GST_VALIDATE_CONFIG': config.name},
                                                'scenarios': ["play_15s"]},
                                            ))



def setup_tests(test_manager, options):
    print("Setting up tests to validate v4l2 playback")
    valid_scenarios = ["play_15s"]
    pipelines_descriptions = []

    add_format_conversion_tests(pipelines_descriptions)
    test_manager.add_expected_issues(EXPECTED_ISSUES)
    test_manager.add_generators(test_manager.GstValidatePipelineTestsGenerator
                                ("validate_elements", test_manager,
                                 pipelines_descriptions=pipelines_descriptions,
                                 valid_scenarios=valid_scenarios))

    return True

