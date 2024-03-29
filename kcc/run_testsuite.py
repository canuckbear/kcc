#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
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


""" This modules implements the functionnalities used to create (from the yaml structure)
and run a test suite, either from top level category or from any midlevel or subcategory.
"""

import logging
import os
from kcc.cli_command import CliCommand
from kcc.model import Key
from kcc.model import TestSuite
from kcc.ansi_colors import Colors

# -----------------------------------------------------------------------------
#
#    Class RunTestuite
#
# -----------------------------------------------------------------------------
class RunTestSuite(CliCommand):
  """This class implements methods needed to load a test suite from the
  configuration files, run it, and sumarize tests resuts.

  Results are display to output according to parameters from the command line.
  These paraeters are stored inthe configurationobject by the CLI parser
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, cfg):
    """Default constructor
    """

    # Initialize ancestor
    CliCommand.__init__(self, cfg)

    # Initialize the hash table used to cache test results
    self.results_cache = {}

    # Current test site. Object used to sore YAML structure loaded from file
    self.suite = None

  # -------------------------------------------------------------------------
  #
  # run_suite
  #
  # -------------------------------------------------------------------------
  def run_suite(self):
    """This method implement the business logic of running a test suite.
    Runing test suite is made of several steps ientified below.

    It calls dedicated method for each step. The main steps are :
    .
    """

    # Check that there is a configuration file first
    if self.cfg is None:
      logging.critical("The configuration file object is not defined")
      exit(1)

    # Instanciate a TestSuite object and load its content from the YAML file
    self.suite = TestSuite()
    self.suite.load(self.cfg.suite)

    # Check that the path to script library is defined (can come from config file or command line)
    if self.cfg.library:
      # Check if global configuration exist, then append it to the current lib
      if self.cfg.configuration is not None and \
         Key.TEST_LIBRARY_PATH.value in self.cfg.configuration:
        # Iterate the list of path from the system confguration file
        for path in self.cfg.configuration[Key.TEST_LIBRARY_PATH.value]:
          # And append the current path to the list used by this application instance
          self.cfg.library.append(os.path.expanduser(path))

      for item in self.cfg.library:
        logging.debug("Using library path : " + item)
    else:
      # Not defined on cli, thus check if defined in config file
      if not Key.TEST_LIBRARY_PATH.value in self.cfg.configuration:
        logging.critical("The library path is not defined")
        exit(1)
      else:
        # Yes, then copy it into self.library
        self.cfg.library = self.cfg.configuration[Key.TEST_LIBRARY_PATH.value]

    # Check that the path to test suite file is defined (can come from config file or command line)
    if self.cfg.suite:
      logging.debug("Using test suite : " + self.cfg.suite)
    else:
      logging.critical("The suite path is not defined")
      exit(1)

    # Check that the path to test suite file is defined (can come from config file or command line)
    if self.cfg.category is None or len(self.cfg.category) == 0:
      # No category given, then add all the root categories
      self.cfg.category = []
      for suite in self.suite.suite:
        self.cfg.category.append(suite[Key.CATEGORY.value])

    # Iterate the list of categories and call the run test category method
    for category in self.cfg.category:
      self.find_category_and_run_test(category)


  # -------------------------------------------------------------------------
  #
  # find_category_and_run_test
  #
  # -------------------------------------------------------------------------
  def find_category_and_run_test(self, category):
    """This method search for the given category, then execute recursively
    all the tst defined at its level, then at the sub level. Category can be
     either the root of the tree, or a sub category.

    The root will be defined as "category", an subcategories as :
      "category:subcategory1:subsubcategory2"
    """

    #
    # Seek the given category in the test tree
    #

    # First let's split the category in its component names (aka tokens)
    tokens = category.split(":")

    # And now let's walk in the tree
    categories = self.suite.suite

    # Counter used to know how many toeksn have been processed so far
    counter = 0

    # Variable used to concatenate category in a path. Join on args from cli is likely to loose case
    # Thus we use data from the YAML test fie
    cat_to_display = ""

    # Iterate the full tokens array
    while counter < len(tokens):

      # Use a flag to know if the search tokens has been found or not
      token_was_found = False

      # Iterate the categories at this level
      for cur in categories:
        # And test if we have fond the searched category
        if cur[Key.CATEGORY.value].lower() == tokens[counter].lower():
          # Mark token as found
          token_was_found = True

          # Push category name to disply variable
          if len(cat_to_display) > 0:
            # Let's add a separator if this categor is not the fist in the display variable
            cat_to_display += ":"

          cat_to_display += cur[Key.CATEGORY.value]

          # Update current category
          if Key.TEST_SUITE.value in cur:
            categories = cur[Key.TEST_SUITE.value]
          else:
            categories = {}
            categories[0] = cur

          # Have we reached the end of the tokens list ?
          if counter == len(tokens) - 1:
            # Yes, thus exit this loop
            categories = {}
            categories[0] = cur
            break
          else:
            # Not yet, let's goo deeper
            continue

      # Check if we have found something or not ?
      if not token_was_found:
        self.cfg.logging.critical("The token " + tokens[counter] + " defined in the category to "
                                  "execute was not found in the test suite definition file")
        exit(1)

      # Increment the tokens counter
      counter += 1

    # Category has been found. Now let's recurse...
    print("[+] " + Colors.FG_YELLOW.value + Colors.BOLD.value + cat_to_display + Colors.RESET.value)
    print("------------------------------------")
    if Key.DESCRIPTION.value in categories[0]:
      print(" " + categories[0][Key.DESCRIPTION.value])
    msg_buffer = []
    self.execute_test_recursively(categories[0], output_msg=msg_buffer)
    print("")



  # -------------------------------------------------------------------------
  #
  # execute_test_recursively
  #
  # -------------------------------------------------------------------------
  def execute_test_recursively(self, category, current_level=0, output_msg=None):
    """This method is in charge of doing real test execution, and recurse down
    to the test tree (going down in the subcategories).
    """

    # Generate a local output buffer
    local_msg = []

    # Generate output string
    output = ""
    output = "".join("  " for i in range(current_level))
    output += " - Testing " + category[Key.CATEGORY.value]

    # Flags used to mark if the locally defined and subcategories tests were successfull
    success_local = True
    success_subtest = True

    # Defines variables used to store stderr and stdout content
    err = None
    out = None

    # Execute test defined at category level
    if not Key.TEST.value in category:
      # No test is defined, only output a deug log and move to nxt category
      logging.debug("No test defined in category " + category[Key.CATEGORY.value])
    else:
      # Let's iterate all the tests in the current category
      for test in category[Key.TEST.value]:
        # Initialize local variables
        ret = -1

        # Now, let's generate the path to the real test. Let'siterate all the path from
        # the library. User defined path have been inserted to head of the array.
        script_found = False

        for item in self.cfg.library:
          # Generate current path
          script_path = item + "/" + test[Key.SCRIPT.value]
          script_path = os.path.expanduser(script_path)

          # Does the file exist ?
          logging.debug("Checking if script " + script_path + " exist and is executable...")
          if os.path.isfile(script_path) and os.access(script_path, os.X_OK | os.R_OK):
            # Yes found it, thus exit the search loop
            logging.debug("Found " + script_path)
            script_found = True
            break

        # Check that the script has been found. Loop can end without positive hit.
        if not script_found:
          logging.error("Script " + script_path +" does not exist. Mark test as failed.")
          ret = -1
        # Script exist, we can try to execute it
        else:
          # If args are defined, concatenate to the script command line
          script_cmd = script_path
          if Key.ARGS.value in test:
            script_cmd += " " + test[Key.ARGS.value]

          # If the cache is activated, then store the result in the hash table
          if self.cfg.use_results_cache:
            logging.debug("Using result cache")
            # Is the value already in cache ? If not then create the sub hashtable
            # Subtable is used to hash arguments for a given script
            if not test[Key.SCRIPT.value] in self.results_cache.keys():
              logging.debug("Create SUB hashtable for " + test[Key.SCRIPT.value])
              self.results_cache[test[Key.SCRIPT.value]] = {}

            # Check if we already have a result for these arguments, if no store the result
            if test[Key.ARGS.value] in self.results_cache[test[Key.SCRIPT.value]].keys():
              logging.debug("Cache hit for " + test[Key.SCRIPT.value] + " " + test[Key.ARGS.value])
              logging.debug("Using previous result " +
                            str(self.results_cache[test[Key.SCRIPT.value]][test[Key.ARGS.value]]))
              ret = self.results_cache[test[Key.SCRIPT.value]][test[Key.ARGS.value]]
            else:
              logging.debug("Cache miss for " + test[Key.SCRIPT.value] + " " + test[Key.ARGS.value])
              logging.debug("Executing test script")
              ret, out, err = self.execute_command(script_cmd)

          else:
            # Not using cache, thus execute the test
            ret, out, err = self.execute_command(script_cmd)

        # Output generation is moved after test execution to be able to output failed test in bold
        # And filter output using the --errors-only flag.
        test_output = ""

        # Generate the output message describing the current test
        test_output = "".join("  " for i in range(current_level))

        # Output the BOLD ANSI sequence
        if ret != 0:
          test_output += Colors.FG_RED.value

        # Check if there is a test description in the YAML file
        if Key.DESCRIPTION.value in test:
          # YEs, thus out the description
          test_output += "   - " + test[Key.DESCRIPTION.value]
        else:
          # No description available, thus default to outputing the test script name
          test_output += "   - Running : " + test[Key.SCRIPT.value]


        # Output the RESET ANSI sequence
        if ret != 0:
          test_output += Colors.RESET.value

        # Concatenate the current test informaton to the output
        test_output += "".join(" " for i in range(Key.OUTPUT_RESULT_PADDING.value - \
                               len(test_output)))

        # And generate the colored result output. Green is a success, red a failure
        if ret == 0:
          success_local &= True
          test_output += "[" + Colors.FG_GREEN.value + Colors.BOLD.value + " OK "
          test_output += Colors.RESET.value + "]"
        else:
          success_local &= False
          test_output += "[" + Colors.FG_RED.value + Colors.BOLD.value + " KO "
          test_output += Colors.RESET.value + "]"

          # Output the returns to the debug log
          logging.debug("Return code : " + str(ret))
          if out is not None:
            logging.debug("Stdout      : " + str(out))
          if err is not None:
            logging.debug("Stderr      : " + str(err))

          # Test failed,check if hinting is activated, if yes, concatenated to output buffer
          if self.cfg.show_hints:
            test_output += "\n"
            test_output += "".join("  " for i in range(current_level))
            test_output += "     " + Colors.FG_CYAN.value + "Hint : "
            test_output += self.show_hints(script_path, ret) + Colors.RESET.value

        # Push the line to output to the message buffer only if below aggregation level
        if self.cfg.aggregation_level is None or (current_level < int(self.cfg.aggregation_level)):
          local_msg.append(test_output)

        # If the cache is activated, then store the result in the hash table
        if self.cfg.use_results_cache:
          logging.debug("Using result cache")
          # Is the value already in cache ? If not then create the sub hashtable
          # Subtable is used to hash arguments for a given script
          if not test[Key.SCRIPT.value] in self.results_cache.keys():
            logging.debug("Create SUB hashtable for " + test[Key.SCRIPT.value])
            self.results_cache[test[Key.SCRIPT.value]] = {}
          else:
            # Check if we already have a result for these arguments, if no store the result
            if not test[Key.ARGS.value] in self.results_cache[test[Key.SCRIPT.value]].keys():
              logging.debug("Cache miss for " + test[Key.SCRIPT.value] + " " + test[Key.ARGS.value])
              self.results_cache[test[Key.SCRIPT.value]][test[Key.ARGS.value]] = ret
            else:
              logging.debug("Cache hit for " + test[Key.SCRIPT.value] + " " + test[Key.ARGS.value])

    # Add string right padding to align at Key.OUTPUT_RESULT_PADDING.value
    output += "".join(" " for i in range(Key.OUTPUT_RESULT_PADDING.value - len(output)))

    # Iterate the sub cateries and recursivly execute tests
    if Key.TEST_SUITE.value in category:
      # For each sub category in the test suite
      for cur in category[Key.TEST_SUITE.value]:
        # Recurse suite tree
        res, out = self.execute_test_recursively(cur, current_level + 1, output_msg)

        # Then use the return values to compute the new subtest state
        success_subtest &= res

        # Concatenate the string buffers
        local_msg += out

    # Were local tests sucessful ? yes thus a green OK
    if success_local:
      if success_subtest:
        output += "[" + Colors.FG_GREEN.value + Colors.BOLD.value + " OK "
        output += Colors.RESET.value + "]"
      else:
        # We have to deal now with the case of "no local tests". If no local test are defined,
        # thus it has to go red and not orange
        if not Key.TEST.value in category:
          output += "[" + Colors.FG_RED.value + Colors.BOLD.value + " KO "
          output += Colors.RESET.value + "]"
        else:
          output += "[" + Colors.FG_ORANGE.value + Colors.BOLD.value + " Partiel "
          output += Colors.RESET.value + "]"
    else:
      # Nope... thus a red KO
      output += "[" + Colors.FG_RED.value + Colors.BOLD.value + " KO " + Colors.RESET.value + "]"

    # Push the line to output to the message buffer only if below aggregation level
    if self.cfg.aggregation_level is None or (current_level < int(self.cfg.aggregation_level)):
      local_msg.insert(0, output)

    # Concatenate local and output buffers
    output_msg = local_msg + output_msg

    # If we are back to top level, the print the message buffer
    if current_level == 0:
      for msg in output_msg:
        print(msg)

    # Return the local test result and the subtest result
    return(success_local & success_subtest, output_msg)



  # -------------------------------------------------------------------------
  #
  # how_hints
  #
  # -------------------------------------------------------------------------
  def show_hints(self, script_path, hint_code):
    """This method is in charge of retreiving the hint string from the script
    givenin arguent. It assumes that the script returned a none zero value,
    and that a hint is defined in command in the script.

    Hints format are :
    # @KCC hint hint_code hit_message

    String hint_message is searched then returned. If no hint is available,
    an aempty string is returned.
    """

    # Check that file exists
    if not os.path.isfile(script_path):
      # Yes found it, thus exit the search loop
      logging.error("Script " + script_path + " does not exist")
      return ""

    # Checkcthat file exists
    if not os.access(script_path, os.R_OK):
      # Yes found it, thus exit the search loop
      logging.error("Script " + script_path + " is not readable")
      return ""

    # We can read the script, now let'search for the hint line in the file. Stop at first match
    for line in open(script_path):
      # Split line into individual words
      tokens = line.split()

      # Need at least five items on the line to be a match candidate
      if len(tokens) > 4:
        # Check that this line structure is somethin like "# @KCC hint hint_code _hint_message"
        if tokens[0] == "#" and tokens[1].lower() == "@kcc" and tokens[2].lower() == "hint" and \
           tokens[3] == str(hint_code):
          # Yes :)  ten its a match, return the end of the line
          return " ".join(tokens[4:])

    # Still here ? then no hint is defined, return an empty string
    return ""
