# -*- coding=utf8 -*-
# !/usr/bin/python

import os
import subprocess
import sys
import tail
import thread
import time
import copy


class ExportProj:
    _sourcePath = ""
    _jsonobj = None
    _platform = ""
    _pack_games = []
    _open_log = False
    _unity_path = ""

    def __init__(self, path, jsonobj):
        self._sourcePath = path
        self._jsonobj = jsonobj
        self._logpath = self._sourcePath + os.sep + "exportlog.log"
        self._batchcmd = [self._jsonobj["unity_path"], '-batchmode', '-projectPath',
                          self._sourcePath, '-nographics',
                          '-executeMethod', "CommandTool.GenWrapFiles",
                          '-logFile', self._logpath, '-quit']

    def _unity_log_tail(self, txt):
        # log = txt.split("\n")
        print("Print Log:" + txt)

    def _tail_thread(self, tail_file):
        print "wait for tail file ... %s" % tail_file

        while True:
            if os.path.exists(tail_file):
                print "Start tail file..... %s" % tail_file
                break

        t = tail.Tail(tail_file)
        t.register_callback(self._unity_log_tail)
        t.follow(s=0.1)

    def _genWrapFiles(self):
        print "开始重新生成 Wrap 文件"
        if os.path.exists(self._logpath):
            os.remove(self._logpath)
        print self._batchcmd

        # new thread to tail log file
        thread.start_new_thread(self._tail_thread, (self._logpath,))

        os.system(" ".join(self._batchcmd))
        # process = subprocess.Popen(self._batchcmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=self._sourcePath)
        time.sleep(5)
        print "Gen wrap files all"
        self._batchcmd[6] = "CommandTool.GenWrapAll"

        os.system(" ".join(self._batchcmd))

        print "Wrap 文件生成成功"

    def _buildGameAssets(self, key):
        print u"开始打包 %s 资源" % key
        self._batchcmd[6] = "CommandTool.BuildAssets"
        if os.path.exists(self._logpath):
            os.remove(self._logpath)
        batchcmd = copy.deepcopy(self._batchcmd)
        batchcmd.append("-platform ios -name %s" % key)
        print " ".join(self._batchcmd)
        thread.start_new_thread(self._tail_thread, (self._logpath,))
        os.system(" ".join(self._batchcmd))
        # process = subprocess.Popen(batchcmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=self._sourcePath)
        print u"%s 资源打包完成" % key

    def genProject(self, basename):
        print u"开始进行打包工作", self._jsonobj["project_path"]
        # print "Gen Wrap Files"
        # self._genWrapFiles()
        # self._buildGameAssets("Main")
        # time.sleep(5)
        # for key in self._jsonobj["pack_game"]:
        #     self._buildGameAssets(key)
        #     time.sleep(5)
        # time.sleep(5)
        print "开始导出Xcode项目",self._sourcePath
        os.system("cd %s" % self._sourcePath + os.sep + "Assets")
        os.system("mkdir StreamingAssets")
        os.system("mv Res_* StreamingAssets")
        os.system("cd StreamingAssets")
        os.system("find ./ -name '*.zip' -exec tar xf {} \\; -print")
        os.system("rm -f Res_*")
        batchcmd = copy.deepcopy(self._batchcmd)
        batchcmd[6] = "CommandTool.BuildXCode"
        print self._sourcePath
        os.chdir(self._sourcePath)
        xcodepath = os.path.pardir + os.sep + basename + "_XCode"
        smallgames = "|".join(self._jsonobj["pack_game"])
        print xcodepath, smallgames
        batchcmd.append(u"-xcodepath %s -smallgames %s" % (xcodepath, smallgames))
        print " ".join(batchcmd)