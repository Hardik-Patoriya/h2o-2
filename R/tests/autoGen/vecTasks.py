##
# Munge Task writers: Slicing, Simple Filter, Compound Filter
##

from GenUtils import *
import itertools, time, datetime

def writeSimpleSliceTestTask(FU, data, dataPath, FUParams):
    TESTNAME, DESCRIPTION = FUParams.split(':')
    DATANAME = data
    DATAPATH = dataPath
    #{0} is DATANAME
    #{1} is FU
    #{2} is DATAPATH
    #{3} is TESTNAME
    with open("githash","rb") as f:
        githash = f.read()
    with open("seed", "rb") as f:
        seed = f.read()
    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    test = """
            ##
            # Author: Autogenerated on {4}
            # gitHash: {5}
            # SEED: {6}
            ##
            source('./findNSourceUtils.R')

            Log.info("======================== Begin Test ===========================")
            {3} <- function(conn) {{
                Log.info("A vector-task R unit test on data <{0}> testing the functional unit <{1}> ")
                Log.info("First slice then apply the functional unit <{1}> ")
                Log.info("Uploading {0}")
                hex <- h2o.uploadFile(conn, locate({2}), "r{0}.hex")
           """.format(DATANAME.replace('-','_'), FU, DATAPATH, TESTNAME.replace('-','_'), st, githash, seed)


    





    cols = makeVec(COLS)
    rows = makeVec(ROWS)
    cR = COLROW.split('|')
    #[rows, cols]
    colRow = [makeVec(cR[1]), makeVec(cR[0])]
    loopCols = convertSeq(filter(lambda a: a in ['0', 0],LOOPCOLS.split(';')))
    loopRows = convertSeq(filter(lambda a: a in ['0', 0], LOOPROWS.split(';')))
    loopColRow = LOOPCOLROW.split('|')
    
    #[(row,col),(row,col),...]
    loopColsRows = list(itertools.product(*[loopColRow[1].split(';'), loopColRow[0].split(';')])) 

    #{0} is cols
    colSlice = """
                slicedHex <- hex[,{0}]
               """
    #{0} is rows
    rowSlice = """
                slicedHex <- hex[{0},]
               """

    colRowSlice = \
               """
                slicedHex <- hex[{0},{1}]
               """
    if cols != '0' and cols != 'c()':
        #{0} is DATANAME
        #{1} is cols to slice by
            test += """
                
                Log.info("Performing a column slice of {0} using these columns: {1}")""".format(DATANAME, escape(cols))
            test += colSlice.format(cols)

    if rows not in ['0',0, '',"","c()", "c(0)"]:
        #{0} is DATANAME
        #{1} is rows to slice by
            
            test += """
                
                    Log.info("Performing a row slice of {0} using these rows: {1}")
                """.format(DATANAME, rows)
            test += rowSlice.format(rows)

    if colRow[0] not in ["c(0)","c()",'c("")',"",'','0',0, 'c("")'] and colRow[1] not in ["c(0)","c()",'c("")',"",'','0',0, 'c("")']:
        #{0} is DATANAME
        #{1} is rows to slice by
        #{2} is cols to slice by
        test += """
                
                    Log.info("Performing a row & column slice of {0} using these rows & columns: {2} & {1}")
                """.format(DATANAME, colRow[0], escape(colRow[1]))
        test += colRowSlice.format(colRow[0], colRow[1])
        
    if not any(x in loopCols for x in ['"0"',"0",'0', 0, '', "", "c()", "c(0)"]): 
        #{0} is DATANAME
        #{1} is loopCols to slice by
        test += """ 
                
                    Log.info("Performing a 1-by-1 column slice of {0} using these columns: {1}")
                """.format(DATANAME, escape(','.join(loopCols)))
        for i in loopCols:
            test += \
                """
                    Log.info("Slicing column {1} from data {0}")
                """.format(DATANAME, escape(i))
            test += colSlice.format(i)

    if not any(x in loopRows for x in ["c(0)","c()",'c("")',"",'','0',0, 'c("")']):
        #{0} is DATANAME
        #{1} is loopRows to slice by
        test += """ 
                
                    Log.info("Performing a 1-by-1 row slice of {0} using these rows: {1}")
                """.format(DATANAME, ','.join(loopRows))
        for i in loopRows:
            test += \
                """
                    Log.info("Slicing row {1} from data {0}")
                """.format(DATANAME, i)
            test += rowSlice.format(i)

    if not any(x in loopColRow[0] for x in ['"0"',"0",'0', '', "", "c()", "c(0)", 'c("")']) or not any(x in loopColRow[1] for x in ['"0"',"0",'0', '', "", "c()", "c(0)", 'c("")']):   
        #{0} is DATANAME
        #{1} is rows to loop over
        #{2} is cols to loop over
        test += """ 
                
                    Log.info("Performing a 1-by-1 combined row & column slice of {0} using these rows & columns: {1} & {2}")
                """.format(DATANAME, escape(','.join(loopColRow[1].split(';'))), escape(','.join(loopColRow[0].split(';'))))
        for i in loopColsRows:
            test += \
                """
                    Log.info("Slicing row {1} and column {2} from data {0}")
                """.format(DATANAME, escape(i[0]), escape(i[1]))
            test += colRowSlice.format(i[0], i[1])

    test += """
            Log.inf("End of test")
            PASSS <<- TRUE
            }}
            PASSS <- FALSE
            conn = new("H2OClient", ip=myIP, port=myPort)
            tryCatch(test_that({1}, {0}(conn)), warning = function(w) WARN(w), error = function(e) FAIL(e))
            if (!PASSS) FAIL("Did not reach the end of test. Check Rsandbox/errors.log for warnings and errors.")
            PASS()""".format(TESTNAME.replace('-','_'), DESCRIPTION)

    return test
