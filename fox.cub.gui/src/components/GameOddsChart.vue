<template>
    <div>
        <highcharts :options="getChartData()"></highcharts>
    </div>

</template>

<script>
import { mapGetters } from "vuex";
import {Chart} from 'highcharts-vue'
import {OddsMixin} from '@/mixins/OddsMixin'

export default {
    mixins: [OddsMixin],
    computed: {
        ...mapGetters([
            "odds"
        ])
    },
    components: {
        highcharts: Chart
    },
    methods: {
        getChartData() {
            return {
                title: {
                    text: "Game odds"
                },
                xAxis: {
                    type: 'datetime',
                },
                chart: {
                    zoomType: 'x'
                },
                series: [{
                    name: 'Home Win',
                    data: this.getMoneylineSeries("home")
                }, {
                    name: 'Draw',
                    data: this.getMoneylineSeries("draw"),
                    visible: false
                }, {
                    name: 'Away Win',
                    data: this.getMoneylineSeries("away"),
                    visible: false
                }, {
                    name: 'Total Under',
                    data: this.getTotalSeries("under"),
                    visible: false
                }, {
                    name: 'Total Over',
                    data: this.getTotalSeries("over"),
                    visible: false
                }],

                plotOptions: {
                    series: {
                        marker: {
                            radius: 2,
                            enabled: true
                        },
                        lineWidth: 1,
                        threshold: null
                    }
                },
            }
        }
    }
}
</script>
