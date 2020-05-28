<template>
<Modal
  v-model="visible"
  :title="title"
  width="800"
  :mask-closable="false"
  :closable="false"
>
  <Form ref="addForm" :model="formItem" :label-width="120" :rules="rules" >
    <Form-item label="名称：" prop="name" >
      <Input v-model="formItem.name" placeholder="名称"></Input>
    </Form-item>
    <Form-item label="出发日期"  >
     <DatePicker type="date" placeholder="请输入出发日期" v-model="formItem.left_date"  style="width: 200px"></DatePicker>
    </Form-item>
    <Form-item label="出发时间"  >
        <CheckboxGroup v-model="formItem.peroid">
            <Checkbox label="0:00-6:00" border></Checkbox>
            <Checkbox label="6:00-12:00" border></Checkbox>
            <Checkbox label="12:00-18:00" border></Checkbox>
            <Checkbox label="18:00-24:00" border></Checkbox>
        </CheckboxGroup>
    </Form-item>
    <Form-item label="车站">
      <Input v-model="formItem.stations"  placeholder="请输入出发站"></Input>
    </Form-item>
    <Form-item label="成员"  >
      <Input v-model="formItem.members"  placeholder="请输入成员"></Input>
    </Form-item>
    <Form-item label="允许部分提交"  >
         <i-switch v-model="formItem.allow_less_member"  />
    </Form-item>    
    <Form-item label="座位"  >
      <Input v-model="formItem.seats"  placeholder="请输入座位"></Input>
    </Form-item>
    <Form-item label="车次"  >
      <Input v-model="formItem.train_numbers"  placeholder="请输入车次"></Input>
    </Form-item>
    <Form-item label="排除车次"  >
      <Input v-model="formItem.except_train_numbers"  placeholder="请输入排除车次"></Input>
      </Form-item>

  </Form>
    <div slot="footer">
        <Button type="primary"  @click="confirmAdd">提交</Button>
        <Button   @click="cancelAdd">取消</Button>
    </div>
</Modal>
</template>
<script>
import {formateDate} from '@/libs/tools'
import axios from '@/libs/api.request'
const defaultFormItem={
        name:'123',
        left_date:'',
        peroid:[],
        stations:'123',
        members:'123',
        allow_less_member:true,
        seats:'123',
        train_numbers:'abc',
        except_train_numbers:'1231',
  }

  var DATE_FORMAT='yyyy-MM-dd hh:mm:ss';
  export default {
    props: {
      isAdd : {
        type: Boolean,
        default: false
      },
      editId: {
        type: String,
        default: ''
      },
      showAdd: {
        type: Boolean,
        default: false
      }
    },
    data(){
      return {
        visible:false,
        formItem: defaultFormItem,
        rules: {
          name: [
            { required: true, message: '名称不能为空', trigger: 'blur' }
          ]

        },
         commitDataForm:{}
      }
    },
    computed: {
      // 计算属性的 getter
      title: function () {
        // `this` 指向 vm 实例
        if (this.isAdd) {
          return "添加"
        } else {
          return "编辑"
        }
      },
    },
    //不能直接通过父组件修改子组件属性
    watch: {
      showAdd(val,oldVal){
        if(val){
          this.makeShowAdd()
        }
      }
    },
    methods: {
      confirmAdd(){
        console.log(this.formItem)  
        this.doSumbit('addForm')  
      },
      doSumbit(name){
          try{
                this.$refs[name].validate((valid) => {
                    console.log("Message",this.$Message)
                    if (valid) {
                        console.log("valid success")

                        try{
                           Object.assign(this.commitDataForm,this.formItem)
                        }catch(error){
                            console.error(error)
                        }
                        if(this.commitDataForm.peroid){
                            this.commitDataForm.peroid=this.commitDataForm.peroid.join(',')
                        }
                        this.commitDataForm.left_date=formateDate(new Date(this.commitDataForm.left_date).getTime(),'YYYY-MM-DD')
                        axios.request({
                            url: 'queryjob/',
                            method:'post',
                            data: this.commitDataForm
                        }).then(r=>{
                            this.$Message.success('Success!');
                            this.clearAdd() 
                        })

                    } else {
                        this.$Message.error('Fail!');
                        console.log("valid fail")
                    }
                })
          }catch(error){
              console.error(error)
          }


      },
      cancelAdd(){
         this.doResetFieldValidate('addForm')
         this.clearAdd()
      },
      doResetFieldValidate(name){
        this.$refs[name].resetFields();
      },
      clearAdd(){
       this.formItem = Object.assign({}, defaultFormItem);
        this.visible = false
        console.log("SHow add",this.showAdd)
        this.$emit("closeAddModal")
      },
      loadConfig(){

      },
      makeShowAdd(){
        this.visible=true
        console.log("Make show add")
        console.log("SHow add",this.showAdd)
      }
    },
      created: function () {
      }
    }
  

</script>
