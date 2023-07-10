import os
import torch
from torch import nn
class A():
    def __init__(self,name:str) -> None:
        """
        name (str):name only dont worry
        """

    def function(seLf,name:str='yunlong')->str:
        return name

class MyClass:
    def __init__(self, name: str, age: int):
        """
        初始化MyClass对象。

        Args:
            name (str): 名字参数，表示对象的名字。
            age (int): 年龄参数，表示对象的年龄。
        """
        self.name = name
        self.age = age

    def some_method(self, count: int) -> str:
        """
        Args:
            count (str): 计数参数，表示一些计数。

        Returns:
            str: 返回一个字符串。
        """
        # 方法实现...
        if count==1:
            return 'yunlong'
        else:
            return 'yunpeng'

sss = MyClass('yun',100)
sss.some_method()