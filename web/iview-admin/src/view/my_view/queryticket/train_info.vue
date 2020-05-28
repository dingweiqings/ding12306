<template>
    <div >
            <Row>
                <Col span="6" :gutter="16">{{trainInfo.left_time}}
                    <Row>
                        <Col span="6">{{trainInfo.left_station}}</Col>
                    </Row>
                </Col>
                <Col span="6" :gutter="16" style="color:red">{{trainInfo.time}}
                        <Row >
                                <Col :offset="6"> <Icon type="md-arrow-round-forward" /></Col>
                                 <Col > {{trainInfo.num}}</Col>
                        </Row>
                </Col>
            
            <Col span="6" :gutter="16">{{trainInfo.arrive_time}}
                    <Row>
                        <Col span="6">{{trainInfo.arrive_station}}</Col>
                    </Row>
            </Col>
            </Row>

    </div>


</template>
<script>
  export default {
    props:{
        trainInfo:{
            type:Object
        }
    // leftDate:'',
    //  leftStation:'',
    //  arrvieStation:'',
    //  leftTime:'',
    //  arriveTime:'',
    //  arriveAtCurrentDay:'',
    }
  }
</script>