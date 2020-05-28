<template>
    <Modal
        v-model="show"
        title="抢票任务"
        @on-ok="ok"
        @on-cancel="cancel">
        <Row>
            <Steps :current="current">
                <Step title="新的"></Step>
                <Step title="开始"></Step>
                <Step title="暂停"></Step>
                <Step title="运行中"></Step>
                <Step title="结束"></Step>
            </Steps>
        </Row>
        <Row style="margin-top:25px;margin-left:150px">
            <Button type="primary" @click="start" style="margin-right:25px">开始任务</Button>
            <Button type="warning" @click="end">结束任务</Button>
        </Row>
 
    </Modal>

</template>
<script>
import axios from '@/libs/api.request'
    export default {
        props:{
          id:'',
          showModal:''  ,
          state:0
        },
        watch:{
            showModal(val,oldVal){
                if(val){
                    this.show=true
                    this.current=this.state
                }
            }
        },
        data () {
            return {
                show:false,
                current:0
            }
        },
        methods: {
            start () {
                axios.request({
                    url: 'queryjob/',
                    method: 'patch',
                    params:{pk:this.id},
                    data: {state: 1}
                }).then(r=>{
                console.log("R",r)
                this.current=1
                })
            },
            end(){
              axios.request({
                    url: 'queryjob/',
                    method: 'patch',
                    params:{pk:this.id},
                    data: {state: 4}
                }).then(r=>{
                console.log("R",r)
                this.current=4
                })
            },
            clearModal(){
                this.show=false
                this.current=0
                this.$emit('closeStateModal')
            },
            ok(){
                this.clearModal()
            },
            cancel(){
                this.clearModal()
            }
        }
    }
</script>