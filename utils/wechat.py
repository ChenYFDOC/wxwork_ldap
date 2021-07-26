import requests
import json
from utils.log import logger
from config import settings
import pypinyin


class Wechat_Client:
    def __init__(self):
        self.token = self.get_token(settings['corpid'], settings['secrete'])

    def get_token(self, corpid, secrete):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(corpid, secrete)
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('获取token结果: ' + json.dumps(data))
        if data['errcode'] == 0:
            return data['access_token']
        else:
            return None

    def get_department_list(self, token):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={}&id='.format(token)
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('获取部门信息:' + json.dumps(data))
        if data['errcode'] == 0:
            return data['department']
        else:
            return []

    def build_tree(self, departments):
        """
        :param departments: 企业微信返回的部门列表
        :return:
            {
                1: {
                    'info': {'id': 1, 'name': '奥术大师多', 'parentid': 0, 'order': 100000000},
                    'children': [2, 3]
                },
                2: {
                    'info': {'id': 2, 'name': '部门1', 'parentid': 1, 'order': 100000000},
                    'children': [4, 5]
                }
                3: {
                    'info': {'id': 3, 'name': '部门2', 'parentid': 1, 'order': 100000000},
                    'children': [6, 7]
                }
                ...
            }
        """
        id_map = {1: {'info': departments[0], 'children': []}}
        for dep in departments[1:]:
            id_map[dep['id']] = {
                'info': dep,
                'children': []
            }

            id_map[dep['parentid']]['children'].append(dep['id'])
        return id_map

    def get_dn(self, dep_tree, depid):
        """
        根据部门id来生成组的dn
        :param dep_tree: 公司的组织架构， 详见build_tree
        :param depid: 部门id
        :return:
        """
        dn = []
        tmp = depid
        while depid in dep_tree:
            dn.append(dep_tree[depid]['info']['name'])
            depid = dep_tree[depid]['info']['parentid']
        for i, v in enumerate(dn):
            dn[i] = ''.join([i[0] for i in pypinyin.pinyin(v, style=pypinyin.NORMAL)])
        prefix = 'cn=' + ',cn='.join(dn)
        return prefix + ",dc=weiwen,dc=com"

    def get_user_dns(self, corp, user):
        """
        根据微信返回的user信息生成dn列表
        :param user:
        :param corp: build tree的结构
        :return:
        """
        dns_list = []
        for department in user['department']:
            group_dn = self.get_dn(corp, department)
            dns_list.append('cn={},'.format(user['userid']) + group_dn)
        return dns_list

    def get_users(self, depid, token, recursive=0):
        """
        获取某个部门的所有员工信息
        :param recursive: 是否获取子部门的员工信息
        :param depid: 部门id
        :param token: 认证token
        :return:
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={}&department_id={}&fetch_child={}'.format(
            token, str(depid), recursive)
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('部门员工信息: ' + json.dumps(data))
        if data['errcode'] == 0:
            return data['userlist']
        else:
            logger.error('获取部门员工失败' + json.dumps(data))
            return []


if __name__ == "__main__":
    wc = Wechat_Client()
    res = wc.get_department_list(wc.token)
    aa = wc.build_tree(res)
    bb = wc.get_dn(aa, 1)
    cc = wc.get_users(1, wc.token)
    pass
