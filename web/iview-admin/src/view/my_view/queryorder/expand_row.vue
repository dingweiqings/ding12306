// table-expand.vue
<style scoped>
    .expand-row{
        margin-bottom: 16px;
        margin-left: 20px
    }
    .col{
        margin-right: 15px
    }
</style>
<template>
    <div>
        <Row class="expand-row">
            <Col :span="span" class="col" >
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col" >
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">-</span>
            </Col>

            <Col  :span="span" class="col" >
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>


            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
            <Col :span="span" class="col">
                <span class="expand-value">{{ row.WZ  }}</span>
            </Col>
        </Row>
        <!-- <table :show-header="true" :cloumns="columns" :data="tableDataArr"></table> -->
    </div>
</template>
<script>
    export default {
        props: {
            row: Object
        },
        watch:{
            tableData(val,oldVal){
                console.log("Table data ",val)
            }
        },
        data(){
            return {
            span:1,
            tableDataArr:[
                {WZ: 123}
            ],
            columns:[
                {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},

                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},

              {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},

                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},

                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},

              {title:"无座",key:"WZ"},
                {title:"无座",key:"WZ"},
              {title:"无座",key:"WZ"},

            ]
            }
        }
    };
</script>