<template>
  <el-table
    v-if="info"
    :data="tableData"
    border
    style="width: 100%"
    :row-key="(row: TableRow) => row.key"
  >
    <el-table-column
      prop="label"
      label="基本信息字段"
      width="180"
      fixed="left"
    />
    <el-table-column
      prop="value"
      label="内容"
      min-width="200"
    />
  </el-table>
  <div v-else style="color: #999; text-align: center;">
    暂无查询结果
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue'
import type { StockInfoResponseItem } from '@/types/stockInfo'
import type{TableRow} from "@/types/common"

const props = defineProps<{
  info: StockInfoResponseItem | null
}>()

// 映射接口字段名到用户友好字段名
const fieldLabelMap: Record<string, string> = {
  exchange_code: '交易所代码',
  exchange_name: '交易所名称',
  org_id: '机构ID',
  org_name_cn: '机构中文名称',
  org_short_name_cn: '机构中文简称',
  org_name_en: '机构英文名称',
  org_short_name_en: '机构英文简称',
  main_operation_business: '主营业务',
  operating_scope: '经营范围',
  district_encode: '地区编码',
  org_cn_introduction: '机构介绍',
  legal_representative: '法人代表',
  general_manager: '总经理',
  secretary: '董事会秘书',
  established_date: '成立日期',
  reg_asset: '注册资本',
  staff_num: '员工人数',
  telephone: '联系电话',
  postcode: '邮编',
  fax: '传真',
  email: '电子邮箱',
  org_website: '官方网站',
  reg_address_cn: '注册地址',
  office_address_cn: '办公地址',
  currency_encode: '货币编码',
  currency: '货币',
  listed_date: '上市日期',
  provincial_name: '省份',
  actual_controller: '实际控制人',
  classi_name: '分类名称',
  pre_name_cn: '前名称',
  chairman: '董事长',
  executives_nums: '高管人数',
  actual_issue_vol: '实际发行量',
  issue_price: '发行价格',
  actual_rc_net_amt: '实际募集净额',
  pe_after_issuing: '发行后市盈率',
  online_success_rate_of_issue: '网上发行中签率',
  affiliate_industry: '所属行业',
}

// 生成表格数据，字段名+值
const tableData = computed(() => {
  if (!props.info) return []
  return Object.entries(props.info).map(([key, val]) => ({
    key,
    label: fieldLabelMap[key] ?? key,
    value: val === null || val === undefined || val === '' ? '-' : val,
  }))
})
</script>

<style scoped>
</style>
