#!/usr/bin/python

import sys
import os
import re
import getopt

scriptName = os.path.basename(__file__).replace('.pyc', '.py')

#================================================================

def usage():
    print("Usage:")
    print(scriptName + " --tracePython logfile_basename")
    print(scriptName + " --tracePython stdout")
    print(scriptName + " --tracePython stdout,logfile_basename")
    print()
    sys.exit(1)

#================================================================

global use_trace_log_file
use_trace_log_file = 0
trace_log_file  = ""

traceLog  = None

send_to_stdout = False

def outputTraceMsg(traceMsg):
    global traceLog
    global msgCount
    global use_trace_log_file
    # global logs_dir
    # if log_file != log_file:
        # open(log_file, "a").write(traceMsg + "\n")

    if send_to_stdout == True:
        print(traceMsg)
    # print use_trace_log_file
    if use_trace_log_file == 0:
        return
    # print ("use_trace_log_file: %d\n" % use_trace_log_file)
    traceLog.write(traceMsg + "\n")

    if use_trace_log_file == 2:
        msgCount += 1
        # print("msgCount: %d\n" % msgCount)
        if msgCount > 1000:
            msgCount = 0
            filesize = os.stat(trace_log_file).st_size
            if filesize >= 10000000:
                if "1.log" in trace_log_file:
                    trace_log_file = tracePythonLogfileBasename + "2.log"
                else:
                    trace_log_file = tracePythonLogfileBasename + "1.log"
                traceLog.write("Switch to " + trace_log_file + "\n")
                traceLog.close()
                traceLog=open(trace_log_file, "w")
                use_trace_log_file = 2

    # print ("use_trace_log_file: %d\n" % use_trace_log_file)
    # else:
        # mikemoto: This still doesn't work.
        # if (hasattr( 'logs_dir')):
            # print logs_dir+"/"+log_file + "\n"
            # open(logs_dir+"/"+log_file, "a").write(traceMsg)


import linecache

# homedir = os.getenv('HOME', 'HOME_var_not_found')

VIRTUAL_ENV_LIB = ''

resumed = False

prev_filename = ''
prev_func_name = ''
prev_lineno = -1
prev_line = ''
prev_watch_var_value = 'not_set'

curr_filename = ''
curr_func_name = ''
curr_lineno = -1
curr_line = ''

def tracefunc(frame, event, arg, indent=[0]):
    global resumed
    global log_file_temp
    global file_num_lines

    global prev_filename
    global prev_func_name
    global prev_lineno
    global prev_line
    global prev_watch_var_value

    global curr_filename
    global curr_func_name
    global curr_lineno
    global curr_line

    # print(90, arg)

    prev_filename = curr_filename
    prev_func_name = curr_func_name
    prev_lineno   = curr_lineno
    prev_line = curr_line

    curr_lineno = frame.f_lineno
    # filename = frame.f_globals["__file__"]
    curr_filename = frame.f_code.co_filename
    if curr_filename == None:
        return tracefunc

    if (curr_filename.endswith(".pyc") or
        curr_filename.endswith(".pyo")):
        curr_filename = curr_filename[:-1]
    # Don't trace Python system libraries.
    # Only trace python scripts in the user's HOME dir tree.  Don't trace Python system libraries.
    # if (not re.search(scriptName, filename)) and (not re.search(homedir, filename)):
    # print scriptName, filename, homedir

    # outputTraceMsg("106 " + filename)
    # outputTraceMsg("107 " + VIRTUAL_ENV_LIB)
    if '/usr/lib' in curr_filename:
        return
    if VIRTUAL_ENV_LIB != '' and VIRTUAL_ENV_LIB in curr_filename:
        return
    if 'bootstrap' in curr_filename:
        return

    line_ID = ''  # 't:'

    curr_filename = os.path.basename(curr_filename)
    curr_line = linecache.getline(curr_filename, curr_lineno).rstrip()
    curr_func_name = frame.f_code.co_name

    if watch_var_name != None and watch_var_name != '':

        if event != "line":
            resumed = False
            if event == "call" or event == "c_call":
                # outputTraceMsg(line_ID + "call>" + filename + ":" + str(lineno) + ":" + curr_func_name)
                # outputTraceMsg(line_ID + "-" * indent[0] + "call>from: " + prev_filename + ", prev_lineno: " + str(prev_lineno) + ", prev_line: " + prev_line + ": to: " + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)
                outputTraceMsg(line_ID + "-" * indent[0] + "call>from: " + prev_filename + ", prev_lineno: " + str(prev_lineno) + ": to: " + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)
                # print "-" * indent[0] + ">call " + curr_func_name + ":"
                # outputTraceMsg(line_ID + "%05d:%s" % (lineno, line.rstrip()))
                indent[0] += 2
            elif event == "return" or event == "c_return":
                # outputTraceMsg(line_ID + "return<" + filename + ":" + str(lineno) + ":" + curr_func_name + ": resuming with " + frame.f_back.f_code.co_filename + ", line " + str(frame.f_back.f_lineno) + ", " + frame.f_back.f_code.co_name)
                # outputTraceMsg(line_ID + "return_from<" + filename + ":" + str(lineno) + ":" + curr_func_name)
                outputTraceMsg(line_ID + "-" * indent[0] + "return_from<" + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)
                # print "<" + "-" * indent[0] + "exit " + curr_func_name
                # print filename + ":" + str(lineno)
                indent[0] -= 2
                resumed = True
            else:
                outputTraceMsg(line_ID + "-" * indent[0] + "unexpected_event="+event+"<" + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)

            prev_watch_var_value = 'not_set'

        else:  # event == 'line'

            if resumed:
                outputTraceMsg(line_ID + "-" * indent[0] + "resumed_with:" + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)
                resumed = False

            max_line_length = 50

            if watch_var_name in prev_line:

                curr_watch_var_value = 'not_set'
                for key,value in dict.items(frame.f_locals):
                    if value == None:
                        continue
                    # print(179, watch_var_name, key)
                    if watch_var_name == key:
                        curr_watch_var_value = value
                        break

                if curr_watch_var_value == 'not_set':

                    for key,value in dict.items(frame.f_globals):
                        if value == None:
                            continue
                        # print(180, watch_var_name, key)
                        if watch_var_name == key:
                            curr_watch_var_value = value
                            break
    
                # print(182, prev_watch_var_value, curr_watch_var_value)
                if curr_watch_var_value == 'not_set':
                    pass
                    # error_message = "ERROR: Filename %s, line %d: watch_var_name in prev_line but curr_watch_var_value not found.  prev_line: %s" % (prev_filename, prev_lineno, prev_line)
                    # outputTraceMsg(error_message)
                    # print(error_message)
                    # sys.exit(1)

                elif prev_watch_var_value == str(curr_watch_var_value):
                    outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_name in prev_line %d:%s.  After curr_line, no change in value" % (prev_lineno, prev_line.rstrip()))
                else:
                    if len(str(curr_watch_var_value)) > max_line_length:
                        line_value = str(curr_watch_var_value)[:max_line_length] + " ... line truncated to " + str(max_line_length) + " chars"
                    else:
                        line_value = str(curr_watch_var_value)
        
                    outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_name in prev_line %d:%s, change in value:" % (prev_lineno, prev_line.rstrip()))
                    outputTraceMsg(line_ID + "-" * indent[0] + "   Old value = '" + str(prev_watch_var_value) + "'")
                    outputTraceMsg(line_ID + "-" * indent[0] + "   New value = '" + line_value + "'")

                    prev_watch_var_value = str(curr_watch_var_value)


            if watch_var_name in curr_line:
           
                curr_watch_var_value = 'not_set'
                for key,value in dict.items(frame.f_locals):
                    if value == None:
                        continue
                    if watch_var_name == key:
                        curr_watch_var_value = value
                        break
 
                if curr_watch_var_value == 'not_set':

                    for key,value in dict.items(frame.f_globals):
                        if value == None:
                            continue
                        # print(180, watch_var_name, key)
                        if watch_var_name == key:
                            curr_watch_var_value = value
                            break
             
                # print(216, prev_watch_var_value, curr_watch_var_value)
                if curr_watch_var_value == 'not_set':
                    # note_message = "NOTE: Filename %s, line %d: watch_var_name in curr_line but value not found.  String in comment?  Substring?  curr_line: %s" % (curr_filename, curr_lineno, curr_line)
                    # outputTraceMsg(note_message)
                    # print(note_message)
                    prev_watch_var_value = 'not_set'

                elif prev_watch_var_value == str(curr_watch_var_value):
                    outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_name in curr_line %d:%s.  After this line, no change in curr_watch_var_value: '%s'" % (curr_lineno, curr_line.rstrip(), curr_watch_var_value))
                else:
                    if len(str(curr_watch_var_value)) > max_line_length:
                        line_value = str(curr_watch_var_value)[:max_line_length] + " ... line truncated to " + str(max_line_length) + " chars"
                    else:
                        line_value = str(curr_watch_var_value)
             
                    outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_name in curr_line %d:%s, change in value:" % (curr_lineno, curr_line.rstrip()))
                    outputTraceMsg(line_ID + "-" * indent[0] + "   Old value = '" + str(prev_watch_var_value) + "'")
                    outputTraceMsg(line_ID + "-" * indent[0] + "   New value = '" + line_value + "'")
                    prev_watch_var_value = str(curr_watch_var_value)


                    # if watch_var_action == 'report_all':
                    #     outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_in_key " + watch_var_name + ": value = " + line_value + ": in file " + curr_filename + ":" + str(curr_lineno) + ":" + curr_func_name)
                    # elif watch_var_action == 'report_changed':
                    #     if curr_watch_var_value == '':
                    #         # print(147, key)
                    #         # print(148, curr_watch_var_value)
                    #         # print(149, value[:max_line_length])
                    #         curr_watch_var_value = str(watch_var_value)
                    #     else:
                    #         if curr_watch_var_value != str(watch_var_value):
                    #             outputTraceMsg(line_ID + "-" * indent[0] + "watch_var_in_key_changed " + watch_var_name + " in file " + prev_filename + ":" + str(prev_lineno) + ":" + prev_func_name)
                    #             outputTraceMsg(line_ID + "-" * indent[0] + "   Old value = '" + str(curr_watch_var_value) + "'")
                    #             outputTraceMsg(line_ID + "-" * indent[0] + "   New value = '" + line_value + "'")
                    #             curr_watch_var_value = str(watch_var_value)
                    #  
                    # else:
                    #    outputTraceMsg(line_ID + "-" * indent[0] + "ERROR: Unrecognized watch_var_action = " + watch_var_action)
                    #    print("ERROR: Unrecognized watch_var_action = " + watch_var_action)
                    #    sys.exit(1)
        
        
    return tracefunc


def enableTrace(trace_options):
    global traceLog
    global trace_log_file
    global use_trace_log_file
    global msgCount
    global send_to_stdout
    global resumed
    global watch_var_name
    global watch_var_action
    global VIRTUAL_ENV_LIB
    global prev_watch_var_value

    watch_var_name = trace_options.get('watch_var_name', None)
    watch_var_action = trace_options.get('watch_var_action', None)
    tracePythonLogfileBasename = trace_options.get('tracePythonLogfileBasename', 'traceLog')
    trace_logfile_type = trace_options.get('trace_logfile_type', 'single_file')

    for output_option in tracePythonLogfileBasename.split(','):
        if output_option == 'stdout':
            send_to_stdout = True
            use_trace_log_file = 0
        else:
            tracePythonLogfileBasename = output_option

    if trace_logfile_type == 'single_file':
        use_trace_log_file = 1
        trace_log_file = tracePythonLogfileBasename + ".log"
        traceLog=open(trace_log_file, "w")
        traceLog.write("Python trace logfile created: %s\n" % trace_log_file)

    else:   # Round-robin switch between two Python trace files.
        use_trace_log_file = 2
        trace_log_file = tracePythonLogfileBasename + "1.log"
        traceLog=open(trace_log_file, "w")
        # print("Python trace logfile created: \n")
        traceLog.write("Python trace logfile created: %s\n" % trace_log_file)
        msgCount = 0  # How often to check the current trace file's size.
        #     print("ERROR:Failed_to_update_EL: %s" % msg ) # Needed by higher-up script
        #     usage(msg)

    VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV','')
    if VIRTUAL_ENV != '':
       VIRTUAL_ENV_LIB = VIRTUAL_ENV + '/lib'
    else:
       VIRTUAL_ENV_LIB = ''

    sys.settrace(tracefunc)
    # sys.setprofile(tracefunc)



#================================================================

def test_func3():
    print("lowest test_func")

def test_func2(param2b, param2a):
    tempvar = "hello"
    test_func3()
    tempvar = "hello"
    tempvar = "hello2"

def test_func1(param1a):
    global tempvar

    tempvar = 'hello1'
    if 2 == 3:
       print('match')

    test_func2(34, param1a)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["tracePython=", "test_trace"])
    except Exception as e:
      # if "option --tracePython requires argument" in e.args:
      #    tracePythonLogfileBasename = "screen"
      # else:
        print("ERROR: Unrecognized runstring option.  e.message: " + e.message + ".  e.args: " + str(e.args))
        usage()

    trace_options = {}

    for opt, arg in opts:
        if opt in ("--tracePython"):
            tracePythonLogfileBasename = arg.strip()
            enableTrace(tracePythonLogfileBasename)

        elif opt == "--test_trace":
            trace_options['watch_var_name'] = 'tempvar'
            trace_options['watch_var_action'] = 'report_change'
            enableTrace(trace_options)

        else:
            print("ERROR: Runstring options.")
            usage()


    param0 = 12
    test_func1(param0)

    print("You can also run the default trace:   python -m trace --trace testfile.py")



