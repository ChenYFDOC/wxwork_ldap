## 同步ad与企业微信  
### 快速搭建  
- 确保环境安装docker，运行项目build_ldap_admin.sh脚本  
- 点击提示地址可进入ldapadmin可视化管理界面（只能本地访问）
- 在项目config里面配置所需信息,各个配置项作用如下：
    - ldap_host：
    - ldap_admin：ldap管理员登录dn
    - ldap_admin_pw：管理员密码
    - corpid：
    - secrete：
    - email_host：发邮件的服务器
    - email_user：邮件的用户登录名
    - email_password：登录密码
    - email_sender：发送者  
### 用法
- 直接运行项目下的main文件，只是检查同步信息并打印log日志
- 加上-a参数可以同步ad服务器，例如python main.py -a
### 注意事项
- 企业微信必须绑定邮箱，否则无法同步进ad服务器
