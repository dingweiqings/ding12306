<template>
    <Tabs value="name1">
        <TabPane label="未完成订单" name="name1">
          标签一的内容
          </TabPane>
        <TabPane label="未出行订单" name="name2">
          标签二的内容
          </TabPane>
        <TabPane label="历史订单" name="name3">
          标签三的内容
          </TabPane>
    </Tabs>
</template>
<script>
import list from './c_list'
  export default {
  name: 'content_page',
  components: {
    list,
    },
  }
</script>