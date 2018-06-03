from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True, verbose_name='资产ID')
    asset_kind = models.ForeignKey('AssetKind', models.DO_NOTHING, blank=True, null=True, verbose_name='资产种类')
    asset_name = models.CharField(max_length=45, verbose_name='资产名称')
    asset_val = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='资产价值')

    def __str__(self):
        return self.asset_name

    class Meta:
        verbose_name = '资产'
        verbose_name_plural = verbose_name + '列表'
        db_table = 'asset'


class AssetDepreciate(models.Model):
    depreciate_id = models.AutoField(primary_key=True, verbose_name='折旧记录ID')
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=True, null=True, verbose_name='操作员工')
    depreciate_date = models.DateTimeField(verbose_name='折旧时间')
    asset = models.ForeignKey(Asset, models.DO_NOTHING, blank=True, null=True, verbose_name='资产ID')
    depreciate_kind = models.ForeignKey('DepreciateKind', models.DO_NOTHING, db_column='depreciate_kind', blank=False,
                                        null=True, verbose_name='折旧种类')
    depreciate_val = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name='折旧价值')
    residual_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, verbose_name='残余价值')

    def __str__(self):
        return 'ID:' + str(self.depreciate_id) + ' ' + str(self.asset) + str(self.depreciate_kind.depreciate_name)

    class Meta:
        verbose_name = '资产折旧记录'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'asset_depreciate'


class AssetKind(models.Model):
    kind_id = models.AutoField(primary_key=True)
    kind_name = models.CharField(max_length=45)

    def __str__(self):
        return self.kind_name

    class Meta:
        verbose_name = '资产种类'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'asset_kind'


class AssetRegister(models.Model):
    register_id = models.AutoField(primary_key=True)
    register_data = models.DateTimeField(verbose_name='登记时间')
    asset = models.ForeignKey(Asset, models.DO_NOTHING, blank=False, null=True, verbose_name='资产')
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=False, null=True, verbose_name='登记员工')
    asset_img = models.ForeignKey('Photo', models.CASCADE, blank=True, null=True)
    initial_price =  models.DecimalField(max_digits=18, decimal_places=2, verbose_name='入库价格')
    class Meta:
        verbose_name = '资产登记记录'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'asset_register'

    def __str__(self):
        return str(self.asset) + str(self.register_data).split()[0]


class AssetRepair(models.Model):
    repair_id = models.AutoField(primary_key=True)
    repair_staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=False, null=True, verbose_name='维修员工')
    repair_time = models.DateTimeField(verbose_name='维修时间')
    repair_asset = models.ForeignKey(Asset, models.CASCADE, blank=False, null=True, verbose_name='维修资产')

    class Meta:
        verbose_name = '资产维修记录'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'asset_repair'

    def __str__(self):
        return self.repair_asset.asset_name


class RepairDetail(models.Model):
    repair_id = models.AutoField(primary_key=True)
    repair_id = models.ForeignKey('AssetRepair', models.CASCADE, verbose_name='维修记录')
    detail_str = models.CharField(verbose_name='维修详情', max_length=1000)

    class Meta:
        verbose_name = '维修记录详情'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'repair_details'

    def __str__(self):
        return self.repair_asset.asset_name


class Photo(models.Model):
    img_id = models.AutoField(primary_key=True)
    img = models.ImageField(upload_to='img/')
    img_name = models.CharField(max_length=30, verbose_name='图片名称')

    class Meta:
        db_table = 'asset_photos'

    def __str__(self):
        return self.img_name




class AssetRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    request_date = models.DateTimeField(verbose_name='申领时间')
    request_return_date = models.DateTimeField(blank=True, null=True, verbose_name='归还时间')
    request_staff_id = models.CharField(max_length=45, blank=False, null=True, verbose_name='申领人')
    asset = models.ForeignKey('Asset', models.DO_NOTHING, blank=False, null=True, verbose_name='资产')
    operator_staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=False, null=True, verbose_name='经办员工')

    class Meta:
        verbose_name = '资产申领记录'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'asset_request'

    def __str__(self):
        return str(self.request_staff_id) + '申领:' + str(self.asset)


class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=45, verbose_name='部门名称')
    dep_permmison = models.ForeignKey(Group, on_delete=models.DO_NOTHING, verbose_name='部门权限')

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name + '列表'
        db_table = 'department'

    def __str__(self):
        return self.dep_name


class DepreciateKind(models.Model):
    depreciate_kind_id = models.AutoField(primary_key=True)
    depreciate_name = models.CharField(max_length=45, null=False, default='unnamed', verbose_name='折旧种类名称')
    depreciate_cal = models.CharField(max_length=45, blank=False, null=False, default='x', verbose_name='折旧表达式(x代表价值)')

    def __str__(self):
        return self.depreciate_name

    class Meta:
        verbose_name = '资产折旧种类'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'depreciate_kind'


class Permission(models.Model):
    per_id = models.IntegerField(primary_key=True)
    per_permission_str = models.CharField(max_length=30)

    class Meta:
        verbose_name = '员工权限'
        verbose_name_plural = verbose_name  # + '列表'
        db_table = 'permission'


class Staff(models.Model):
    staff_name = models.CharField(max_length=40, verbose_name='员工姓名')
    staff_id = models.AutoField(primary_key=True, verbose_name='员工ID')
    staff_dep = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True, verbose_name='所属部门')
    staff_user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='对应的帐号', blank=False, null=True)
    staff_img = models.OneToOneField('Photo', on_delete=models.CASCADE, verbose_name='员工照片', blank=False, null=True)
    # staff_user = models.OneToOneField('users.User', on_delete=models.CASCADE, verbose_name='对应的帐号', blank=False, null=True)

    def __str__(self):
        return self.staff_name

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = verbose_name + '列表'
        db_table = 'staff'


class InviteCode(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='邀请码ID')
    times = models.IntegerField(verbose_name='剩余次数')
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部门')
    key = models.CharField(max_length=100, verbose_name='邀请码')
    ddl_time = models.DateTimeField(verbose_name='过期时间')
    operator_staff = models.ForeignKey('Staff', models.CASCADE, blank=False, null=True, verbose_name='发放用户')

    class Meta:
        verbose_name = '邀请码'
        verbose_name_plural = verbose_name


'''
class User(models.Model):
    username = models.CharField(primary_key=True, max_length=16)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=32)
    create_time = models.DateTimeField()

    # staff = models.ForeignKey(Staff, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'user'
'''
