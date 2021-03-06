# coding: utf-8

import os
import glob
import re
from abc import abstractmethod, ABC


"""
日志分析器。
"""
class LogParser(ABC):

    def __init__(self, root, unknown=True, verbose=True):
        """

        :param root: 日志根目录
        :param unknown: 是否只解析未匹配成功户型（暂时只支持True)
        :param verbose:
        """
        self.root = root
        self.unknown = unknown  # TODO
        self.verbose = verbose

    def __call__(self):
        return self.parser()

    def search(self):
        dirs = []
        files = glob.glob(os.path.join(self.root, '*'))
        for file in files:
            if os.path.isdir(file):
                dirs.append(file)
        return dirs

    def find_suit_dirs(self):
        dirs = self.search()
        pat = re.compile('(.*\d+_\d+)')
        suitable_dirs = list(map(lambda x: pat.findall(x), dirs))
        return self.flat_l(suitable_dirs)

    @abstractmethod
    def parser(self):
        pass

    @staticmethod
    def flat(L):
        for ele in L:
            if isinstance(ele, list):
                yield from LogParser.flat(ele)
            else:
                yield ele

    @staticmethod
    def flat_l(L):
        return list(LogParser.flat(L))


class LogParserFail(LogParser):

    def __init__(self, *args, **kwargs):

        kwargs['unknown'] = True

        super().__init__(*args, **kwargs)

    def parser(self, save=False):
        """

        :param save: 是否保存解析结果 # TODO
        :return:
        """
        dirs = self.find_suit_dirs()
        for dir in dirs:
            per_dir_files = glob.glob(os.path.join(dir, '*.json'))
            if self.verbose:
                print('-'.center(50, '-'))

            tmp_set_not_success = set()  # 用于去重

            for per in per_dir_files:
                pat = re.compile('.*?(\d+)_(\d+)')
                pat2 = re.compile('\]-(.[^-_]+?)[_-]')
                if self.unknown:

                    if '未知' in per:
                        solution_id, dna_Solution_id = pat.findall(dir)[0]
                        name = pat2.findall(per)[0]

                        tmp_set_not_success.add((solution_id,
                                                 dna_Solution_id,
                                                 name))

            for ele in tmp_set_not_success:
                solution_id, dna_Solution_id, name = ele
                if self.verbose:
                    print('匹配失败户型: ', solution_id,
                          '被匹配DNA:', dna_Solution_id,
                          '户型名称: ', name)


class LogParserSuccess(LogParser):

    def __init__(self, *args, **kwargs):

        kwargs['unknown'] = False

        super().__init__(*args, **kwargs)

    def parser(self, save=False):
        """

        :param save: 是否保存解析结果 # TODO
        :return:
        """
        dirs = self.find_suit_dirs()
        for dir in dirs:
            per_dir_files = glob.glob(os.path.join(dir, '*.json'))
            if self.verbose:
                print('-'.center(50, '-'))

            tmp_set_success = set()

            for per in per_dir_files:
                pat = re.compile('.*?(\d+)_(\d+)')
                pat2 = re.compile('\]-(.[^-_]+?)[_-]')
                if 'best' in per and '未知' not in per:
                    solution_id, dna_Solution_id = pat.findall(dir)[0]
                    pat3 = re.compile("_(\d[.]\d{0,2})_(\d[.]\d{0,2})")
                    pat4 = re.compile("\]_(\w+)_\w+")
                    name = pat4.findall(per)[0].split("_")[0]
                    score1, score2 = pat3.findall(per)[0]
                    tmp_set_success.add((solution_id, dna_Solution_id,
                                         name, score1, score2))

            for ele in tmp_set_success:
                solution_id, dna_Solution_id, name, score1, score2 = ele
                if self.verbose:
                    print("匹配成功户型：", solution_id,
                          "被匹配DNA: ", dna_Solution_id,
                          "户型名称: ", name,
                          "score1: ", score1,
                          "score2：", score2)


if __name__ == "__main__":
    root = 'log'
    parser = LogParserSuccess(root)
    parser()
