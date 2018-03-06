# -*- coding=UTF-8 -*-
"""Test `link_maya` module.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from unittest import TestCase, main, skip


class LinkMayaTestCase(TestCase):
    def setUp(self):
        from wlf.cgtwq import Database
        self.filename = 'D:\\Users\\zhouxuan.WLF\\Desktop\\SNJYW_EP26_05_sc238.mb'
        self.database = Database('proj_big')
        self.references = ['Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_E/rig/SNJYW_QiFuShiWei_E_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset_work/sets/SNJYW_JJFHY_YanHuiTai/model/lo/ok/SNJYW_JJFHY_YanHuiTai_Lo.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset_work/character/SNJYW_MingHuoSheng/rig/lo/ok/SNJYW_MingHuoSeng_Lo.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei/rig/SNJYW_QiFu_ShiWei_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_B/rig/SNJYW_QiFuShiWei_B_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_D/rig/SNJYW_QiFuShiWei_D_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_E/rig/SNJYW_QiFuShiWei_E_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei/rig/SNJYW_QiFu_ShiWei_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_B/rig/SNJYW_QiFuShiWei_B_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_C/rig/SNJYW_QiFuShiWei_C_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_D/rig/SNJYW_QiFuShiWei_D_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_QiFu_ShiWei_E/rig/SNJYW_QiFuShiWei_E_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_XC_BengDai/rig/SNJYW_XC_BengDai_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_JN_TaoHua/rig/SNJYW_JN_TaoHua_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_XuYongNing/rig/SNJYW_DGG_XuYongNing_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_JN_BaoBao/rig/SNJYW_JN_BaoBao_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_HD_BianFu/rig/SNJYW_HuangDi_BianFu_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset_work/character/SNJYW_WangTong/rig/lo/ok/SNJYW_WangTong_Lo.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset_work/character/SNJYW_QiChengGuang_BianFuA/rig/lo/ok/SNJYW_QiChengGuang_BianFuA_Lo.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_WenGuanA/rig/SNJYW_WenGuan_A_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_WenGuanB/rig/SNJYW_WenGuanB_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_YQ_JingYeWei_A/rig/SNJYW_YQ_JingYeWei_A_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_YQ_JingYeWei_B/rig/SNJYW_YQ_JingYeWei_B_Hi.mb',
                           'Z:/CGteamwork_Test/SNJYW/asset/character/SNJYW_YXT_ShiWei/rig/SNJYW_YXT_ShiWei_Hi.mb']

    @skip('Read maya file will takes a very long time.')
    def test_get_reference(self):
        from link_maya import get_references
        result = get_references(self.filename,self.database)
        self.assertEqual(result, self.references)

    def test_get_asset(self):
        from link_maya import get_assets

        result = get_assets(self.references,self.database)
        expected = (u'00E3E8E1-6216-6D98-F171-0B697FDD8C73', u'305', u'306', u'318',
                    u'7DCE9C8F-A6E5-F5B6-D5AE-F0D823E39165', u'90583E95-BCC8-E087-9DE3-1E0001ABFB9B',
                    u'BD357610-D964-643C-5D50-2CFEB86E16BC', u'C129CB85-B7AF-33FB-E801-C516941E8023',
                    u'DB941307-CAD0-834E-9AEC-FB790E6E4BD0', u'DFF5E3F5-EDB3-EB7B-B7E9-ACD24155563B',
                    u'EDE119C5-8071-67BE-0F1F-CFBF5F5CD270')
        self.assertEqual(result, expected)

    @skip('Read maya file will takes a very long time.')
    def test_link_asset(self):
        from link_maya import link_assets
        link_assets('5E6F49E5-A677-3292-2436-16D4FBBECDE3',self.database)


if __name__ == '__main__':
    main()
