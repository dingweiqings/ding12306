<style lang="less">
  @import './register.less';
</style>

<template>
  <div class="register">
    <div class="register-con">
      <Card icon="register-in" title="欢迎注册" :bordered="false">
        <div class="form-con">
          <register-form @on-success-valid="handleSubmit"></register-form>
        </div>
      </Card>
    </div>
  </div>
</template>

<script>
import RegisterForm from '_c/register-form'

import axios from '@/libs/api.request'
export default {
  components: {
    RegisterForm
  },

  methods: {
    handleSubmit (form) {
      console.log("Register form",form)
      axios.request({
          url: 'account/register/',
          method: 'post',
          data: form
        }).then(r=>{
          this.$Message.success("注册成功,请登录")
          this.$router.push({
              name:'login',
              params: 
              { username: form.username,
              password: form.password 
              }
            })   
        })
    
    }
  }
}
</script>

<style>

</style>
