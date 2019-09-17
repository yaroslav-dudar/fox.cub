<template>
    <div>
        <highcharts :options="getChartData()"></highcharts>
    </div>

</template>

<script>
import {Chart} from 'highcharts-vue'
export default {
    props: ['data', 'title'],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartData() {
            return {
                title: {
                    text: this.title
                },
                xAxis: {
                    type: 'datetime',
                },
                yAxis: {
                    title: {
                        text: 'Exchange rate'
                    }
                },
                chart: {
                    type: 'spline',
                    zoomType: 'x'
                },
                series: [{
                    name: 'Odds',
                    data: this.data,
                }],

                plotOptions: {
                    area: {
                        fillColor: {
                            linearGradient: {
                                x1: 0, y1: 0,
                                x2: 0, y2: 1
                            }
                        },
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
