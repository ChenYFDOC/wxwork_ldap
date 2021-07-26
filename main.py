from utils.ad import LDAP_Client
from utils.wechat import Wechat_Client
from utils.log import logger
import password_generator
from collections import defaultdict
from utils.send_email import Sender


def get_groups_from_ldap(client):
    ad_groups = defaultdict(bytes)  # ad上的group信息
    for i in client.search('dc=weiwen,dc=com', 'objectClass=posixGroup'):
        ad_groups[i[0].lower()] = i[1]
    return ad_groups


def get_users_from_ldap(client):
    ad_users = defaultdict(bytes)
    for i in client.search('dc=weiwen,dc=com', 'objectClass=posixAccount'):
        user_dn = i[0]
        ad_users[user_dn] = i
    return ad_users


def run(fix=True):
    adclient = LDAP_Client()
    wxclient = Wechat_Client()
    sender = Sender()  # 邮件发送器

    # 获取微信的组织结构
    res = wxclient.get_department_list(wxclient.token)
    corp = wxclient.build_tree(res)

    ad_users = get_users_from_ldap(adclient)  # ad上的user
    ad_groups = get_groups_from_ldap(adclient)  # ad上的组

    for k in corp.keys():
        # 验证ad组是否存在(某个部门是否存在对应的ad组)
        dn = wxclient.get_dn(corp, k)
        if dn.lower() in ad_groups:
            del ad_groups[dn.lower()]
        else:
            logger.info('用户组' + dn + '在ad中不存在')
            if fix:
                adclient.add_group(dn)

    # 确定用户是否存在
    users = wxclient.get_users(1, wxclient.token, recursive=1)
    for u in users:
        u_dns = wxclient.get_user_dns(corp, u)
        for u_dn in u_dns:
            if u_dn in ad_users:
                ad_users.pop(u_dn)
            else:
                if fix and u['email'] and not adclient.exists('mail=' + u['email']):
                    logger.info('用户' + u['name'] + '在ad中不存在')
                    password = password_generator.generate(length=10)
                    adclient.add_user(u_dn, password, u['email'])
                    logger.info('用户' + u['name'] + '已添加进ad')
                    sender.send('你的通用账号为：{}\n你的通用密码为：{}'.format(u['userid'], password), u['email'])

    # 处理ad端多余的用户和组
    for k in ad_groups.keys():
        logger.info('用户组 {} 只在AD中存在'.format(k))
        if fix:
            adclient.delete(k)

    for k in ad_users.keys():
        logger.info('用户 {} 只在AD中存在'.format(k))
        if fix:
            adclient.delete(k)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='是否需要同步ad服务器')
    parser.add_argument('-a', dest='bool_', action='store_true', help='sync mode')
    args = parser.parse_args()
    run(fix=args.bool_)  # fix传True代表需要同步ad服务器
