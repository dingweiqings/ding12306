<template>
  <div>
    <Card>
      <Button style="margin: 10px 0;" type="primary" @click="exportExcel">导出为Csv文件</Button>
    <Button style="margin: 10px 0;" type="primary" @click="showAddMethod">添加</Button>
    <div  class="search-con search-con-top">
      <Select v-model="query.leftStation" style="width:200px" placeholder="出发站" filterable clearable >
        <Option v-for="item in cityList" :value="item.key" :key="item.name" >{{ item.name }}</Option>
      </Select>
      <Select v-model="query.arriveStation" style="width:200px" placeholder="终点站" filterable clearable>
        <Option v-for="item in cityList" :value="item.key" :key="item.name" >{{ item.name }}</Option>
      </Select>
      <DatePicker type="date" placeholder="请输入出发日期" v-model="query.leftDate"  style="width: 200px"></DatePicker>
      <Button @click="handleSearch" class="search-btn" type="primary"><Icon type="search"/>&nbsp;&nbsp;搜索</Button>
    </div>
      <tables ref="tables" editable searchable search-place="top" v-model="tableData" :columns="columns" 
      :total="total"
      @on-delete="handleDelete"
      @changePageSize="changePageSize"
      @changePage="changePage"
      />
    </Card>
    <add @reloadPage="loadData()" :showAdd="showAdd" :isAdd="isAdd" :editId="editId" @closeAddModal="closeAddModal">  </add>
    <c-state @closeStateModal="closeStateModal"  :id="editId" :showModal="showState" :state="state"></c-state>
  </div>
</template>

<script>
import Tables from '_c/tables'
import add from './add'
import axios from '@/libs/api.request'
import CState from './c_state'
export default {
  name: 'tables_page',
  components: {
    Tables,add,CState
  },
  data () {
    return {
      total:0,
      editId:'',
      cityList:[],
      state:0,
      columns: [
        { title: '出发日期', key: 'left_date' },
        { title: '出发车站', key: 'left_station' },
        { title: '到达车站', key: 'arrive_station' },
        { title: '列车号', key: 'train_number' },
       { title: '状态', key: 'state' ,
         render: (h, params) => {
            let span_text=''
            if(params.row.state==0){
              span_text='新的'
            }else if(params.row.state==1){
              span_text="开始"
            }else if(params.row.state==2){
              span_text="运行中"
            }else if(params.row.state==3){
              span_text='暂停'
            }else if(params.row.state==4){
              span_text='结束'
            }
            return h('div', [
                          h('Span', span_text),
                    ]);
        }
       },
        {
          title: '操作',
          key: 'handle',
          button: [
           (h, params, vm) => {
              return h('Icon', {
                 style: {
                     cursor:'pointer'
                  },
                  props: {
                    type:'md-hammer'
                  },
                on: {
                  'click': () => {
                    this.showState=true
                    this.state=params.row.state
                    this.editId=params.row.id
                  }
                }
              })
            }
          ]
        }
      ],
      tableData: [],
      showAdd:false,
      isAdd:true,
      editId:'',
      showState:false,
      query:{
        leftStation:'',
        arriveStation:'',
        leftDate:'',
        page:1,
        page_size:10,
        searchValue:'',
        orderBy:'createtime',
        direction:'ASC'
      }
    }
  },
  methods: {
      loadData(){
          axios.request({
              url: 'queryjob/',
              method: 'get',
              params: this.query
          }).then(r=>{
            console.log("R",r)
            this.tableData=r.data.results
            console.log("table data",this.tableData)
            this.total=r.data.count
          })
      },
      closeStateModal(){
        this.showState=false
        this.loadData()
      },
      closeAddModal(){
        this.showAdd=false 
        console.log("Show add",this.showAdd)
        this.loadData()
      },
      showAddMethod(){
        this.showAdd=true
        console.log("List Show add",this.showAdd)
      },
    handleDelete (params) {
      console.log(params)
    },
    exportExcel () {
      this.$refs.tables.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
    },
    getTableData(){

    },
    changePage(page){
      console.log("Change page list")
        this.query.page=page
        this.loadData()
        console.log("this.query",this.query.page)
    },
    changePageSize(size){
        this.query.page_size=size
        console.log("Page size",this.query.page_size)
        this.loadData()
    },
    handleSearch(){
        this.query.page=1
        this.loadData()
    },
    loadCityList(){
      axios.request({
              url: 'queryticket/citylist/',
              method: 'get',
              params: this.query
          }).then(r=>{
            console.log("R",r)
            this.cityList=r.data.data
      })
    }
  },
  mounted () {
    this.getTableData()
    this.loadCityList()
    this.loadData()

  }
}
</script>

<style>

</style>
