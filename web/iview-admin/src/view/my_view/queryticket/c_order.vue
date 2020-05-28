<template>
    <Modal
        v-model="show"
        title="预订"
        :closable="false"
        >
      <Form ref="form" :model="form" :rules="rule" inline>
        <FormItem label="车次">
            <Input type="text" v-model="form.num" disabled style="color:red">
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
         <FormItem label="出发日期">
            <Input type="text" v-model="form.left_date" disabled style="color:red">
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem label="出发站" >
            <Input type="text" v-model="form.left_station" disabled style="color:black">
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem  label="终点站">
            <Input type="text" v-model="form.arrive_station" disabled style="color:black">
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem  label="出发时间" style="color:black">
            <Input type="text" v-model="form.left_time" disabled>
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem label="到达时间" style="color:black">
            <Input type="text" v-model="form.arrive_time" disabled >
                <Icon type="ios-lock-outline" slot="prepend"></Icon>
            </Input>
        </FormItem>
        <FormItem label="当日到达" style="color:black;margin-right:150px" >
           <i-switch v-model="form.arrive_at_current_day" disabled></i-switch>
        </FormItem>
        <FormItem label="座位" prop="seat">
            <Select v-model="form.seat" style="width:200px"   placeholder="座位" > 
                    <Option v-for="item in seatArr" :value="item.name" :key="item.name" :label="item.name">{{ item.name +"  "+item.num}}</Option>
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
    const defaultForm={
        trainNum:'',
        left_date:'',
        left_station:'',
        arrive_station:'',
        left_time:'',
        arrive_time:'',
        arrive_at_current_day:'',
        seat:'',
        passengers:''
    }
    export default {
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
           showModal:''  ,
           seatArr:{
               type:Array
           },
           passengersArr:{
               type:Array
           }
        },
        
        watch:{
            showModal(val,oldVal){
                if(val){
                    console.log("Cc order ",this.trainInfo)
                    Object.assign(this.form,this.trainInfo)
                    console.log("Cc order form",this.form)
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
                        { required: true, message: '请选择座位', trigger: 'blur' }
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
                            this.commitDataForm.left_date=this.form.left_date.substring(0,4)+"-"+this.form.left_date.substring(4,6)+"-"+this.form.left_date.substring(6)
                            this.commitDataForm.seat=this.form.seat
                            this.commitDataForm.passengers=this.form.passengers
                            this.commitDataForm.secret_str=this.form.secret_str
                            this.commitDataForm.left_station=this.form.left_station
                            this.commitDataForm.arrive_station=this.form.arrive_station
                        }catch(error){
                            console.error(error)
                        }
                        axios.request({
                            url: 'queryticket/order/',
                            method:'post',
                            data: this.commitDataForm
                        }).then(r=>{
                            this.$Message.success('Success!');
                            this.clearModal() 
                        })

                    } else {
                        this.$Message.error('Fail!');
                        console.log("valid fail")
                    }
                })
            },
            clearModal(){
                this.show=false
                this.form.passengers=''
                this.form.seat=''
                this.$emit('closeOrderModal')
            },
            cancel(){
                this.clearModal()
            },
            handleSeatArr(){

            },
            loadPassagengers(){
                axios.request({
                    url: 'queryticket/passengers/',
                    method:'get',
                }).then(r=>{
                    this.passengersArr=r.data.data
                    console.log("load passgengers ",r)
                })
            },
            loadSeatArr(){
                    
            }

        }
    }
</script>