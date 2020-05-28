<template>
  <div>
    <div  class="search-con search-con-top">
    <Select v-model="query.leftStation" style="width:200px" placeholder="出发站" filterable clearable >
      <Option v-for="item in cityList" :value="item.key" :key="item.name" >{{ item.name }}</Option>
    </Select>
    <Select v-model="query.arriveStation" style="width:200px" placeholder="终点站" filterable clearable>
      <Option v-for="item in cityList" :value="item.key" :key="item.name" >{{ item.name }}</Option>
    </Select>
    <DatePicker type="date" placeholder="请输入出发日期" v-model="leftDate"  style="width: 200px"></DatePicker>
    <Input  placeholder="请输入车次" v-model="query.trainNum"  style="width: 200px"></Input>
    <Button @click="handleSearch" class="search-btn" type="primary"><Icon type="search"/>&nbsp;&nbsp;搜索</Button>
  </div>
    <Card>
      <Table  :data="tableData" :columns="columns" @on-expand="handleExpand">

      </Table>
    </Card>
    <add @reloadPage="loadData()" :showAdd="showAdd" :isAdd="isAdd" :editId="editId" @closeAddModal="closeAddModal">  </add>
    <c-order @closeStateModal="closeStateModal"  :trainInfo="trainInfo" :showModal="showState" :seatArr="seatArr"></c-order>
  </div>
</template>

<script>
import Tables from '_c/tables'
import expandRow from './expand_row'
import add from './add'
import axios from '@/libs/api.request'
import COrder from './c_order'
import {formateDate} from '@/libs/tools'
import {getAtCurrentDay,getSeatPriceTypes,getSeatArr}  from '@/libs/util'
export default {
  name: 'tables_page',
  components: {
    Tables,add,COrder,expandRow,
  },
  data () {
    return {
      total:0,
      editId:'',
      leftDate:'',
      trainInfo:{},
      cityList:[],
      seatArr:[],
      priceRow:{},
      rowIndex:0,
      columns: [
          { type: 'expand',
                        width: 50,
                        render: (h, params) => {
                            return h(expandRow, {
                                props: {
                                    row: this.priceRow
                                }
                            })
                        }
                    },

        { title: '车次', key: 'num', sortable: true ,
          filters: [
              {
                  label: '高铁',
                  value: 'G'
              },
              {
                  label: '动车',
                  value: 'D'
              },
              {
                  label: '普快',
                  value: 'K'
              },
              {
                  label: '特快',
                  value: 'T'
              },
               {
                  label: '直达',
                  value: 'Z'
              },
          ],
          filterMultiple: true,
          filterMethod (value, row) {
              console.log("Value ",value)
              return row.num.indexOf(value)>=0
          }
        },
        { title: '出发站', key: 'left_station' },
        { title: '终点站', key: 'arrive_station' },
   //     { title: '出发日期', key: 'left_date' },
        { title: '出发时间', key: 'left_time',

          filters: [
              {
                  label: '0-6 ',
                  value: 6
              },
              {
                  label: '6-12',
                  value: 12
              },
              {
                  label: '12-18 ',
                  value: 18
              },
              {
                  label: '18-24',
                  value: 24
              }
          ],
          filterMultiple: false,
          filterMethod (value, row) {
              console.log("Value ",value)
              let starttime=row.left_time.split(":")[0]
              return starttime <value && starttime >value-6
          }
                        },
        { title: '到达时间', key: 'arrive_time',
        
                  filters: [
              {
                  label: '0-6 ',
                  value: 6
              },
              {
                  label: '6-12',
                  value: 12
              },
              {
                  label: '12-18 ',
                  value: 18
              },
              {
                  label: '18-24',
                  value: 24
              }
          ],
          filterMultiple: false,
          filterMethod (value, row) {
              console.log("Value ",value)
              let starttime=row.left_time.split(":")[0]
              return starttime <value && starttime >value-6
          }
        
        },
        { title: '历时', key: 'time' },
        { title: '是否当日到达', key: 'arrive_at_current_day',
        
        render: (h, params) => {
              let arr=[]
              let iconType=''
              if(params.row.arrive_at_current_day){
                  iconType='ios-checkmark-circle'
              }else{
                iconType='md-close-circle'
              }
              return h('div', [
                                  h('Icon', {
                                      props: {
                                          type: iconType,
                                          size: 25
                                      }
                                  }),
                      ]);
          }
        },
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
        { title: '其他', key: 'other' },
        {
          title: '操作',
          key: 'handle',
          render: (h, params) => {
            if(params.row.ops==='预订'){
              return h('div', [
                h('Icon', {
                  style: {
                      cursor:'pointer'
                    },
                    props: {
                      type:'md-hammer'
                    },
                  on: {
                    'click': () => {
                      console.log("Abc ",params.row)
                        let index=-1
                        this.tableData.forEach((e,i)=>{
                          if(e.num===params.row.num){
                            index=i
                          }
                        })
                      Object.assign(this.trainInfo,params.row)
                      this.trainInfo.secret_str=this.tableData[index].secret_str
                      console.log("Assign success ",this.trainInfo)
                      this.seatArr=getSeatArr(params.row)
                      console.log("seat arr",this.seatArr)
                      this.showState=true
                    }
                  }
                })
              ]);
            }else{
                            return h('div', [
                h('Span', params.row.ops)
              ]);
            }

          }
      }
      ],

      tableData: [],
      showAdd:false,
      isAdd:true,
      editId:'',
      showState:false,
      query:{
        page:1,
        leftStation:'HFH',
        arriveStation:'SZH',
        page_size:10,
        searchValue:'',
        trainNum:'',
        leftDate:'',
        orderBy:'createtime',
        direction:'ASC'
      }
    }
  },
  methods: {
    handleExpand(row,status){
      
      let index=-1
      this.tableData.forEach((e,i)=>{
         if(e.num===row.num){
           index=i
         }
      })
      let train_no=this.tableData[index].no
      let seat_types=this.tableData[index].seat_types
      let from_station_no=this.tableData[index].from_station_no
      let to_station_no=this.tableData[index].to_station_no
      let train_date=formateDate(new Date(this.leftDate).getTime(),'YYYY-MM-DD')
      axios.request({
              url: 'queryticket/price/',
              method: 'get',
              params:{
                    train_no: train_no,
                    from_station_no: from_station_no,
                    to_station_no: to_station_no,
                    seat_types: seat_types,
                    train_date: train_date
              }
          }).then(r=>{
            console.log("R",r.data.data.data)
            this.priceRow=r.data.data.data
            console.log("price row",this.priceRow)
           // this.cityList=r.data.data
      })

      console.log("Index",index)
      console.log("NO",this.tableData[index].no)
    },
      loadData(){
        this.query.leftDate=formateDate(new Date(this.leftDate).getTime(),'YYYY-MM-DD')
        console.log("Format date",this.query.leftDate)
          axios.request({
              url: 'queryticket/ticket/',
              method: 'get',
              params: this.query
          }).then(r=>{
            console.log("R",r)
            this.tableData=r.data.data
            console.log("table data",this.tableData)
          })
      },
      closeStateModal(){
        this.showState=false
       // this.loadData()
      },
      closeAddModal(){
        this.showAdd=false 
        console.log("Show add",this.showAdd)
      //  this.loadData()
      },
      showAddMethod(){
        this.showAdd=true
        console.log("List Show add",this.showAdd)
      },
    handleDelete (params) {
      console.log(params)
    },
    getTableData(){

    },
    handleSearch(){
        //this.query.searchValue
        this.loadData()
    } ,
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
  }
}
</script>

<style>

</style>
