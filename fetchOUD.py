# fetchOUD.py
# This script implements an automated procedure to fetch audit files
# from an OUD. Please put the needed info to fetchOUD.conf that has to be
# placed at the same directory
#
# author : Tasos Adamopoulos email: adamopanast@gmail.com
#

import paramiko
import time
import re
from time import sleep



#this method merges all fetched csv files to one - OUD

def OUDmergeAllToOneCsv(finalFileName,fileNames,lPath):
    fileNames.sort()
    fileNames.sort(key= lambda s: len(s))
    outputFileError = lPath + finalFileName +'OUD_ERROR' + '.csv'
    outputFileAdmin = lPath + finalFileName + 'OUD_ADMIN' + '.csv'
    outputFileAccess = lPath + finalFileName + 'OUD_ACCESS' + '.csv'
    outputFileReplication = lPath + finalFileName + 'OUD_REPLICATION' + '.csv'
    fileNamesError = []
    fileNamesAdmin = []
    fileNamesAccess = []
    fileNamesReplication = []
    for name in fileNames:
        if 'error' in name:
            fileNamesError.append(name)
        if 'admin' in name:
            fileNamesAdmin.append(name)
        if 'access' in name:
            fileNamesAccess.append(name)
        if 'replication' in name:
            fileNamesReplication.append(name)
    OUDmerge(outputFile=outputFileAccess,fileNames=fileNamesAccess,columns='TIMESTAMP,TYPE,CONNECTION ID,ATTRIBUTES\n',lPath=lPath)
    OUDmerge(outputFile=outputFileError,fileNames=fileNamesError,columns='TIMESTAMP,CATEGORY,SEVERITY,ATTRIBUTES\n',lPath=lPath)
    OUDmerge(outputFile=outputFileAdmin,fileNames=fileNamesAdmin,columns='TIMESTAMP,TYPE,CONNECTION ID,ATTRIBUTES\n',lPath=lPath)
    OUDmerge(outputFile=outputFileReplication,fileNames=fileNamesReplication,columns='TIMESTAMP,CATEGORY,SEVERITY,MESSAGE_ID,ATTRIBUTES\n',lPath=lPath)


def OUDmerge(outputFile,fileNames,columns,lPath):
    lineCount = 0
    output = open(outputFile, 'w+')
    output.write(columns)
    print('processing...')
    for name in fileNames :
        inputFile = lPath + name +'.csv'
        with open(inputFile,'r') as fp:
            for line in fp:
                lineCount += 1
                output.write(line)
    print('Merge completed . Wrote %d lines to %s (sorted by date)'%(lineCount,outputFile))

def OUDlogToCsv(lPath, fileName,type):
    inputFile = lPath + fileName
    outputFile = inputFile + '.csv'
    output = open(outputFile, 'w+')
    print('input file name:%s\noutput file name:%s\n' % (inputFile, outputFile))
    linesCount = 0
    print('processing....')
    if type == 'access':
        with open(inputFile, 'r') as fp:
            for line in fp:
                linesCount += 1
                line = re.sub('] ', '],', line)
                line = re.sub('conn=', ',\t', line)
                line = re.sub('from',',from',line)
                line = re.sub('reason',',reason',line)
                output.write(line)
    if type == 'admin':
        with open(inputFile, 'r') as fp:
            for line in fp:
                linesCount += 1
                line = re.sub('] ', '],\t', line)
                line = re.sub(' conn=', '\t,', line)
                line = re.sub('from', ',from', line)
                line = re.sub('op', ',op', line)
                output.write(line)
    if type == 'error':
        with open(inputFile, 'r') as fp:
            for line in fp:
                linesCount += 1
                line = re.sub('category=', ',\t', line)
                line = re.sub('severity=', ',\t', line)
                line = re.sub('msgID', ',\tmsgID', line)
                output.write(line)
    if type == 'replication':
        with open(inputFile, 'r') as fp:
            for line in fp:
                linesCount += 1
                line = re.sub('"', ' ', line)
                line = re.sub('category=', ',\t', line)
                line = re.sub('severity=', ',\t', line)
                line = re.sub('msgID=', ',\t', line)
                line = re.sub('msg=',',\t"',line)
                line = re.sub('\n','"\n',line)
                output.write(line)
            
    print('`%s` successfully transformed to `%s` . Wrote %d lines \n\n' % (inputFile, outputFile, linesCount))

#this method transferts a file placed in rPath to lPath

def getFile(lPath, rPath, fileName, connection):
    sleep(0.2)
    localPath = lPath + fileName
    remotePath = rPath + fileName
    connection.get(remotepath=remotePath, localpath=localPath)
    print('copying %s to %s...'%(fileName,lPath))

def main():

# open fetchOUD.conf

    with open('fetchOUD.conf') as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    remoteConnections = []
    remoteConnection = {}
    numberOfTargets = content[5]

# append variables from conf

    line = 9
    weekStartDateStr = content[line]
    line += 3
    weekEndDateStr = content[line]
    line += 3
    for i in range(0,int(numberOfTargets)):
        remoteConnection = {}
        remoteConnection['host'] = content[line]
        print(remoteConnection['host'])
        line +=3
        remoteConnection['cots'] = content[line]
        print('------------%s'%remoteConnection['cots'])
        line += 3
        remoteConnection['usrnm'] = content[line]
        line += 3
        remoteConnection['psswrd'] = content[line]
        line += 3
        remoteConnection['port'] = content[line]
        line +=3
        remoteConnection['rPath'] = content[line]
        remoteConnections.append(remoteConnection)
        line +=4
    lPath = content[line]
    print(remoteConnections)

    print('\nConfig file is accepted... trying to connect to:')

# open connection using paramiko

    for target in range (0,int(numberOfTargets)):
        print('%s:%s (COTS: %s) with credentials: \nusername: %s , password: %s\nremote path :%s\nlocal path: %s' % (
            remoteConnections[target]['host'],remoteConnections[target]['port'],remoteConnections[target]['cots'],remoteConnections[target]['usrnm'],remoteConnections[target]['psswrd'], remoteConnections[target]['rPath'], lPath))
        print('fetch files for time period between: %s - %s\n\n' % (weekStartDateStr, weekEndDateStr))
        try:
            transport = paramiko.Transport(( remoteConnections[target]['host'], int(remoteConnections[target]['port'])))
            transport.connect(username=remoteConnections[target]['usrnm'], password=remoteConnections[target]['psswrd'])
            sftp = paramiko.SFTPClient.from_transport(transport)
        except paramiko.ssh_exception.SSHException:
            print('Host : %s is unreachable. Exit.... \n'%(remoteConnections[target]['host']))
            return
        except:
            print('an error occured. Exit...\n')
            return
        fileNames = []
        fileCount = 0
        finalFileName = ''
    # generate time structs from string dates

        startDate = time.strptime(weekStartDateStr,'%d/%m/%Y')
        endDate = time.strptime(weekEndDateStr, '%d/%m/%Y')

    # get the directory's list, generate every files date from EPOC
    # and check if the file created between the given dates. If it is
    # the file name will be stored at fileNames.

        for fileattr in sftp.listdir_attr(remoteConnections[target]['rPath']):
            fileDate =time.localtime(fileattr.st_mtime)
            if fileDate < endDate and fileDate > startDate :
                fileNames.append(fileattr.filename)
                fileCount += 1

# the files with the collected file names will be fetched

        print('\n%d files will be transfered from host\n'%fileCount)
        for name in fileNames:
            getFile(lPath=lPath,rPath=remoteConnections[target]['rPath'],connection=sftp,fileName=name)

        print('\n%d files successfully transfered from %s\n\n'%(fileCount,remoteConnections[target]['host']))

    # the fetched log files will be converted to csv

        if remoteConnections[target]['cots'] == 'OUD':
            for name in fileNames:
                if 'access' in name:
                    OUDlogToCsv(lPath=lPath,fileName=name,type='access')
                if 'admin' in name:
                    OUDlogToCsv(lPath=lPath,fileName=name,type='admin')
                if 'error' in name:
                    OUDlogToCsv(lPath=lPath, fileName=name, type='error')
                if 'replication' in name:
                    OUDlogToCsv (lPath=lPath, fileName=name, type='replication')

        finalFileName = ('merged_audit_%s_%s-%s'%(remoteConnections[target]['host'],remoteConnections[target]['cots'],target))

        if remoteConnections[target]['cots'] == 'OUD':
            OUDmergeAllToOneCsv(finalFileName=finalFileName,fileNames=fileNames,lPath=lPath)

if __name__ == "__main__":
    main()
