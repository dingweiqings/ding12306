// table-expand.vue
<style scoped>
    .expand-row{
        margin-bottom: 16px;
    }
    .ivu-table-row .demo-table-info-row td{
        background-color: #2db7f5;
        color: #fff;
    }
    .ivu-table-row .demo-table-error-row td{
        background-color: #ff6600;
        color: #fff;
    }
    .ivu-table td.demo-table-info-column{
        background-color: #2db7f5;
        color: #fff;
    }
    .ivu-table .demo-table-info-cell-name {
        background-color: #2db7f5;
        color: #fff;
    }
    .ivu-table .demo-table-info-cell-age {
        background-color: #ff6600;
        color: #fff;
    }
    .ivu-table .demo-table-info-cell-address {
        background-color: #187;
        color: #fff;
    }
</style>
<template>
  <div>
    <Row class="expand-row">
      <Table border :row-class-name="rowClassName" :columns="columns" :data="tableData"></Table>
    </Row>
  </div>
</template>
<script>
    export default {
        props: {
            tableData: Array
        },
        data(){
            return {
            span:1,
            columns:[
            { title: '商务座/特等座', key: 'bussiness_seat' },
            { title: '一等座', key: 'one_seat' },
            { title: '二等座', key: 'two_seat' },
            { title: '高级软卧', key: 'high_soft_sleeper' },
            { title: '软卧/一等卧', key: 'soft_sleeper' },

            { title: '动卧', key: 'dong_sleeper' },
            { title: '硬卧/二等座', key: 'hard_sleeper' },
            { title: '软座', key: 'soft_seat' },
            { title: '硬座', key: 'hard_seat' },
            { title: '无座', key: 'no_seat'},
            ]
            }
        },
        methods:{
            rowClassName (row, index) {
                console.log("Index",index)
                return 'demo-table-error-row';
            }
        }
    };
</script>