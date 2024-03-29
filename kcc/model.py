#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2023 KCC project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

""" This module contains the definition of the constants used in the kcc tool,
and the definition of the configuration clsss. The class implements the methods
used to load its content fom yaml configuration file.
"""

import os
import logging
from enum import Enum
import yaml


# -----------------------------------------------------------------------------
#
# class Key
#
# -----------------------------------------------------------------------------
class Key(Enum):
  """This class defines the valid keys to used to access infrmation from
  confiugration files. The keys are enumerated vlues defined by string. The string
  used are (understand 'must be') the same as the keys in yaml files.

  No string should be manipulated directly, only enum values
  """

  # Define each and every key and associated string used in the tool
  AGGREGATION_LEVEL = "aggregation_level"
  ARGS = "args"
  CATEGORY = "category"
  CHECK_LIBRARY = "check-library"
  CHECK_SUITE = "check-suite"
  FAIL_FAST = "fail_fast"
  LIBRARY = "library"
  LOG_LEVEL = "log_level"
  LOG_LEVEL_INFO = "INFO"
  NO_RESULT_CACHE = "no_result_cache"
  ONLY_ERRORS = "only_errors"
  OPT_AGGREGATION_LEVEL = "--aggregation-level"
  OPT_CATEGORY = "--category"
  OPT_FAIL_FAST = "--fail-fast"
  OPT_HELP_COMMAND = "Command to execute"
  OPT_LIBRARY = "--library"
  OPT_LOG_LEVEL = "--log-level"
  OPT_ONLY_ERRORS = "--only-errors"
  OPT_SUITE = "--suite"
  OPT_SHOW_HINTS = "--show-hints"
  OPT_NO_RESULT_CACHE = "--no-result-cache"
  RUN_SUITE = "run"
  SCRIPT = "script"
  DESCRIPTION = "description"
  SUITE = "suite"
  SHOW_HINTS = "show_hints"
  TEST = "test"
  TEST_LIBRARY_PATH = "test_library_path"
  TEST_SUITE = "test-suite"
  TEST_SUITE_PATH = "test_suite_path"
  UTF8 = "utf-8"
  OUTPUT_RESULT_PADDING = 75


# -----------------------------------------------------------------------------
#
# class Configuration
#
# -----------------------------------------------------------------------------
class Configuration(object):
  """This class defines default configuration for kcc

  The tool configuration contains environment variables used to define
  information such as default working path, etc.

  The values stored in this object are read from the following sources,
  in order of priority (from the highest priority to the lowest).
  """

  # ---------------------------------------------------------------------------
  #
  # __init__
  #
  # ---------------------------------------------------------------------------
  def __init__(self, filename=None):
    """
    """

    # Default configuration file to use if none is provided through the cli
    if filename is None:
      self.filename = "~/.kccrc"
    else:
      self.filename = filename

    # Initialize the defaultlogger
    self.logging = logging.getLogger()

    # Defult log level used
    self.log_level = "warning"

    # Contains the configuration loaded from the YAML file
    self.configuration = None

    # Defines the path to the test suite file
    self.suite = None

    # Floag used to know if we have to display the hints or not
    self.show_hints = None

    # Defines the path to the directory containing the test scripts
    self.library = None

    # Defines the member variables storing the test categories to execute
    self.category = None

    # Defines the ggreation level of tests. Default value is None, which means no aggreation
    # The full test tree is output
    self.aggregation_level = None

    # Flag used to mark if result cache is deactivate.
    # If cache is activated, a given script with a given set of arguments can be run only once.
    # If cache is deactivated, the same script with the same arguments can be run many times
    # A given script with different arguments will always run several time (once per set of
    # diffrent argument values)
    self.use_results_cache = True

  # ---------------------------------------------------------------------------
  #
  # load_configuration
  #
  # ---------------------------------------------------------------------------
  def load_configuration(self, filename=None):
    """ This method load the tool configuration from the given YAML file
    """

    # If a new filename has been passed as argument, then store it
    if filename is not None:
      self.filename = filename

    # Expend ~ as uer home dir
    self.filename = os.path.expanduser(self.filename)

    # Check if configuration file exist in home ir, otherwise switch to package config file
    if not os.path.isfile(self.filename):
      self.filename = "/etc/kcc/kccrc"

    try:
      # Check it the configuration file exist
      if os.path.isfile(self.filename):
        # Yes then, load it
        with open(self.filename, 'r') as working_file:
          self.configuration = yaml.load(working_file)

          # Now we may have to expand a few paths...
          # First check if the configurationis really defined
          if self.configuration is not None:
            # First let's process test_suite_path
            if Key.TEST_SUITE_PATH.value in self.configuration:
              # Check if path starts with ~ and need expension
              self.configuration[Key.TEST_SUITE_PATH.value] = \
                          os.path.expanduser(self.configuration[Key.TEST_SUITE_PATH.value])

    # Catch all OSError exceptions that may have occured. Mostly file errors...
    except OSError as exception:
      # Call clean up to umount /proc and /dev
      self.logging.critical("Error: " + exception.filename + "- " + exception.strerror)
      exit(1)

# -----------------------------------------------------------------------------
#
# class TestSuite
#
# -----------------------------------------------------------------------------
class TestSuite(object):
  """This class defines a test suite. It contains a hierachical structure
  describing the tests to execute, the associated tests scripts and the
  arguments to be passed. A test suite is linked to a suite file, which is a
  YAML description of this object.

  This class provides method needed to load the test description.
  """

  # ---------------------------------------------------------------------------
  #
  # __init__
  #
  # ---------------------------------------------------------------------------
  def __init__(self, filename=None):
    """
    """

    # Default configuration file to use if not provided to load method
    self.filename = None
    if filename is not None:
      self.filename = filename

    # Initialize the defaultlogger
    self.logging = logging.getLogger()

    # Suite definition loaded from the YAML file
    self.suite = None



  # ---------------------------------------------------------------------------
  #
  # load
  #
  # ---------------------------------------------------------------------------
  def load(self, filename=None):
    """ This method load the test suite definition from the given YAML file
    """

    # If a new filename has been passed as argument, then store it
    if filename is not None:
      self.filename = filename

    # Test if the filename to load is defined
    if self.filename is None:
      self.logging.critical("The YAML test-suite file is not defined. Aborting.")
      exit(1)

    # Expand home prefix to have an absolute path
    if self.filename[0] == "~" and self.filename[1] == "/":
      self.filename = os.path.expanduser(self.filename)

    try:
      # Check it the configuration file exist
      if os.path.isfile(self.filename):
        # Yes then, load it
        with open(self.filename, 'r') as working_file:
          self.suite = yaml.load(working_file)
      else:
        # No then output an error
        self.logging.critical("The file " + self.filename + " does not exist. Aborting.")
        exit(1)

    # Catch all OSError exceptions that may have occured. Mostly file errors...
    except OSError as exception:
      self.logging.critical("Error: " + exception.filename + "- " + exception.strerror)
      exit(1)
