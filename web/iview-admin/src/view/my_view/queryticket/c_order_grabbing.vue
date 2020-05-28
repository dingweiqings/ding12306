<template>
    <Modal
        v-model="show"
        title="抢票"
        :closable="false"
        >
      <Form ref="form" :model="form" :rules="rule" inline>
        <FormItem label="车次">
            <Select v-model="form.num" style="width:200px" multiple  placeholder="车次" filterable> 
                    <Option v-for="item in numArr" :value="item.num" :key="item.num" :label="item.num">
                         <train-info :trainInfo="item"> </train-info>
                    </Option>
            </Select>
        </FormItem>
         <FormItem label="出发日期">
            <DatePicker type="date" v-model="form.left_date" multiple  >
   
            </DatePicker>
        </FormItem>
        <FormItem label="出发站" >
            <Input type="text" v-model="form.left_station"  disabled >
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem  label="终点站">
            <Input type="text" v-model="form.arrive_station" disabled>
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem label="座位" prop="seat">
            <Select v-model="form.seat" style="width:200px" multiple  placeholder="座位"> 
                    <Option v-for="item in seatArr" :value="item.name" :key="item.name">{{ item.name}}</Option>
                </Select>
        </FormItem>
        <FormItem label="乘车人" prop="passengers">
            <Select v-model="form.passengers" style="width:200px"  multiple placeholder="乘车人"> 
            <Option v-for="item in passengersArr" :value="item.name" :key="item.name">{{ item.name }}</Option>
        </Select>
        </FormItem>
    </Form>
    <div slot="footer">
        <Button type="primary" @click="handleSubmit('form')">提交</Button>
        <Button   @click="cancel">取消</Button>
    </div>
    </Modal>

</template>
<script>
import axios from '@/libs/api.request'
import TrainInfo from './train_info'
import {formateDate} from '@/libs/tools'
    const defaultForm={
        num:'',
        left_date:[],
        left_station:'',
        arrive_station:'',
        left_time:'',
        arrive_time:'',
        arrive_at_current_day:'',
        seat:'',
        passengers:''
    }
    export default {
        components: {
            TrainInfo
        },
        props:{
         trainInfo:{
             type:Object
         }   ,
        // leftDate:'',
        //  leftStation:'',
        //  arrvieStation:'',
        //  leftTime:'',
        //  arriveTime:'',
        //  arriveAtCurrentDay:'',
           leftDate:'',
           showModal:''  ,
           seatArr:{
               type:Array
           },
           numArr:{
               type:Array
           },
           passengersArr:{
               type:Array
           }
        },
        
        watch:{
            showModal(val,oldVal){
                if(val){
                    console.log("Cc grabbing ",this.trainInfo)
                    Object.assign(this.form,this.trainInfo)
                    this.form.left_date=[]
                    this.form.left_date.push(this.trainInfo.left_date)
                    console.log("watch",this.form.left_date)
                    console.log("Cc grabbing form",this.form)
                    this.form.num=[]
                    this.form.num.push(this.trainInfo.num)
                    // this.form.leftDate=this.leftDate
                    // this.form.leftStation=this.leftStation
                    // this.form.arrvieStation=this.arrvieStation
                    // this.form.leftTime=this.leftTime
                    // this.form.arriveTime=this.arriveTime
                    // this.form.arriveAtCurrentDay=this.arriveAtCurrentDay
                    this.show=true
                }
            }
        },
        data () {
            return {
                show:false,
                form: defaultForm,
                commitDataForm:{},
                rule: {
                    seat: [
                        { required: true, message: '请选择座位', trigger: 'blur',type:'array' }
                    ],
                    passengers: [
                        { required: true, message: '请选择乘客', trigger: 'blur' ,type:'array'},
                    ]
                }
            }
        },
        methods: {
            handleSubmit(name){
                console.log("This form",this.form)
                this.$refs[name].validate((valid) => {
                    console.log("Message",this.$Message)
                    if (valid) {
                        console.log("valid success")
                        try{
                           this.commitDataForm.trainNum=this.form.num
                           this.commitDataForm.left_date=[]
                           console.log("left date",this.form.left_date)
                           this.form.left_date.forEach((e,i)=>{
                                let train_date=formateDate(new Date(e).getTime(),'YYYY-MM-DD')
                                this.commitDataForm.left_date.push(train_date)
                                console.log("this.commitDataForm.left_date.",this.commitDataForm.left_date)
                           })
                            this.commitDataForm.seat=this.form.seat
                            this.commitDataForm.passengers=this.form.passengers
                            this.commitDataForm.left_station=this.form.left_station
                            this.commitDataForm.arrive_station=this.form.arrive_station
                        }catch(error){
                            console.error(error)
                        }
                        axios.request({
                            url: 'querytask/',
                            method:'post',
                            data: this.commitDataForm
                        }).then(r=>{
                            this.$Message.success('Success!');
                            this.clearModal() 
                        })
                        //this.$router.push("/queryjob/queryjob_page")
                    } else {
                        this.$Message.error('Fail!');
                        console.log("valid fail")
                    }
                })
            },
            clearModal(){
                this.show=false
                Object.assign(defaultForm,this.form)
                this.$emit('closeGrabbingModal')
            },
            cancel(){
                this.clearModal()
            },
            handleSeatArr(){

            },

            loadSeatArr(){
                    
            }

        }
    }
</script>