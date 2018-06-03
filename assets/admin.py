from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.contrib.admin.actions import delete_selected
from django.utils.translation import ugettext_lazy

admin.site.site_header = '资产管理系统'
admin.site.site_title = '资产管理系统'


@admin.register(AssetDepreciate)
class AssetDepreciateAdmin(admin.ModelAdmin):
    sub_class = '测试'

    class SafeDeleteQuerysetWrapper(object):
        def __init__(self, wrapped_queryset):
            self.wrapped_queryset = wrapped_queryset
            self.verbose_name = '资产折旧记录'
            self.verbose_name_plural = '资产折旧记录列表'

        def _safe_delete(self):
            for obj in self.wrapped_queryset:
                obj.delete()

        def __getattr__(self, attr):
            if attr == 'delete':
                return self._safe_delete
            else:
                return getattr(self.wrapped_queryset, attr)

        def __iter__(self):
            for obj in self.wrapped_queryset:
                yield obj

        def __getitem__(self, index):
            return self.wrapped_queryset[index]

        def __len__(self):
            return len(self.wrapped_queryset)

    fieldsets = (
        ("资产信息", {'fields': ['asset']}),
        ("折旧信息", {'fields': ['depreciate_date', 'depreciate_kind']})
    )
    list_display = ('asset', 'depreciate_kind', 'depreciate_val', 'residual_value', 'depreciate_date', 'staff')
    list_filter = ['depreciate_kind', 'staff', 'asset']
    search_fields = ('asset__asset_name', 'depreciate_kind__depreciate_name')

    def save_model(self, request, obj, form, change):
        x = float(obj.asset.asset_val)
        func = obj.depreciate_kind.depreciate_cal
        val = eval(func)
        obj.residual_value = val
        obj.depreciate_val = x - obj.residual_value
        obj.staff = request.user.staff
        obj.asset.asset_val = val
        obj.asset.save()
        obj.save()

    def get_actions(self, request):
        actions = super(AssetDepreciateAdmin, self).get_actions(request)
        actions['delete_selected'] = (AssetDepreciateAdmin.action_safe_bulk_delete, 'delete_selected',
                                      ugettext_lazy("Delete selected %(verbose_name_plural)s"))
        return actions

    def action_safe_bulk_delete(self, request, queryset):
        for obj in queryset:
            obj.asset.asset_val = float(obj.depreciate_val) + float(obj.asset.asset_val)
            obj.asset.save()

        wrapped_queryset = AssetDepreciateAdmin.SafeDeleteQuerysetWrapper(queryset)
        return delete_selected(self, request, wrapped_queryset)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'asset_name', 'asset_val', 'asset_kind', 'repair', 'depreciate', 'request', 'register')
    list_filter = ['asset_kind']
    search_fields = ('asset_name', 'asset_id')
    list_display_links = ('asset_id', 'asset_name')

    # readonly_fields = ('asset_id',)

    def save_model(self, request, obj, form, change):
        # 自定义操作
        # print(obj, request, form, change)
        obj.save()

    def repair(self, obj):
        result = AssetRepair.objects.filter(repair_asset=obj)
        return format_html('<a href="/admin/assets/assetrepair/?q={} ">{}</a>', obj.asset_name, str(len(result)))

    def depreciate(self, obj):
        result = AssetDepreciate.objects.filter(asset=obj)
        return format_html('<a href="/admin/assets/assetdepreciate/?q={} ">{}</a>', obj.asset_name, str(len(result)))

    def request(self, obj):
        result = AssetRequest.objects.filter(asset=obj)
        return format_html('<a href="/admin/assets/assetrequest/?q={} ">{}</a>', obj.asset_name, str(len(result)))

    def register(self, obj):
        result = AssetRegister.objects.filter(asset=obj)
        return format_html('<a href="/admin/assets/assetregister/?q={} ">{}</a>', obj.asset_name, str(len(result)))

    repair.short_description = '维修记录数'
    depreciate.short_description = '折旧记录数'
    request.short_description = '申领记录数'
    register.short_description = '资产登记数'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    # list_display = ('staff_id', 'staff_name', 'username', 'last_login','staff_dep')
    search_fields = ('staff_name', 'staff_id')
    list_display_links = ('staff_id', 'staff_name')

    def get_list_display(self, request):
        if request.user.is_superuser:
            self.list_display = ('staff_id', 'staff_name', 'username', 'last_login', 'staff_dep', 'image_tag')
        else:
            self.list_display = ('staff_id', 'staff_name', 'username_nolink', 'last_login', 'staff_dep', 'image_tag')
        return self.list_display

    def username(self, obj):
        username = obj.staff_user.username
        return format_html('<a href="/admin/auth/user/?q={}">{}</a>', username, username)

    def username_nolink(self, obj):
        username = obj.staff_user.username
        return username

    def last_login(self, obj):
        return obj.staff_user.last_login

    def group(self, obj):
        return obj.staff_dep.name

    def save_model(self, request, obj, form, change):
        obj.staff_user.groups.clear()
        if obj.staff_dep:
            obj.staff_user.groups.add(obj.staff_dep.dep_permmison)
        obj.save()

    def image_tag(self, obj):
        try:
            return format_html(
                u'<a href="%s"><img src="%s" height="64" width="48"/></a>' % (
                obj.staff_img.img.url, obj.staff_img.img.url))
        except:
            return format_html('<font color="red">暂无照片</color>')

    image_tag.short_description = u'员工照片'
    username.short_description = u'用户名'
    username_nolink.short_description = u'用户名'
    last_login.short_description = u'上次登录时间'


@admin.register(AssetRegister)
class AssetRegisterAdmin(admin.ModelAdmin):
    search_fields = ('asset__asset_name',)
    list_display = ('asset', 'staff', 'initial_price', 'register_data', 'image_tag',)

    def image_tag(self, obj):
        try:
            return format_html(u'<a href="%s"><img src="%s" height="50" width="50"/></a>' % (
            obj.asset_img.img.url, obj.asset_img.img.url))
        except:
            return format_html('<font color="red">暂无照片</color>')

    image_tag.short_description = u'图片'


@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    search_fields = ('asset__asset_name', 'request_staff_id', 'operator_staff__staff_name')
    list_display = ('asset', 'request_staff_id', 'operator_staff', 'request_date', 'return_state')

    fieldsets = (
        ("资产信息", {'fields': ['asset']}),
        ("申领信息", {'fields': ['request_staff_id', 'request_date']}),
        ("归还信息", {'fields': ['request_return_date']}),
    )

    def return_state(self, obj):
        if obj.request_return_date:
            return format_html('<font color="green">已归还</color>')
        else:
            return format_html('<font color="red">未归还</color>')

    return_state.short_description = '归还状态'

    '''
    def get_readonly_fields(self, request, obj=None):
    if request.user.is_superuser:
        self.readonly_fields = []
    else:
        self.readonly_fields = ['operator_staff']
    return self.readonly_fields
    '''


@admin.register(AssetRepair)
class AssetRepairAdmin(admin.ModelAdmin):
    search_fields = ['repair_asset__asset_name', ]
    list_display = ['repair_asset', 'repair_time', 'repair_staff']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    fieldsets = (
        ("邀请码权限信息", {'fields': ['dept']}),
        ("有效性", {'fields': ['times', 'ddl_time']}),
    )

    list_display = ['dept', 'times', 'ddl_time', 'key', 'status']

    def save_model(self, request, obj, form, change):
        import random
        import base64
        obj.operator_staff = request.user.staff
        # print base64.b64decode(a)
        obj.save()
        random_key = str(random.random())[2:20]
        # print(obj.id)
        key = base64.b64encode(str.encode(str(obj.id) + ' ' + random_key))
        obj.key = key.decode()
        obj.save()

    def status(self, obj):
        if obj.times:
            return format_html('<font color="green">有效</color>')
        else:
            return format_html('<font color="red">失效</color>')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass


admin.site.register(AssetKind)
admin.site.register(DepreciateKind)

# Register your models here.
