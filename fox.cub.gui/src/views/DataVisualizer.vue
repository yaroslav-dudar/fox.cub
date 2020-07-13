<template>
    <div>
        <h3>Select file</h3>
        <input type="file" @change="onFileChange">

        <select v-model="data_field" @change="redraw()">
            <option
                v-for="field in game_attrs" :key="field"
                v-bind:value='field'> {{field}}
            </option>
        </select>
        <hr>

        <div class="pure-g">
            <div class="pure-u-2-5">
                <team-results v-bind:games="games"
                              v-bind:extra_metric="extra_metric"></team-results>
            </div>
            <div class="pure-u-3-5" >
                <highcharts :options="chart_options" style="height: 400px;"></highcharts>
                <histogram-chart :dataset="team_dataset"></histogram-chart>
                <histogram-chart :dataset="opponent_dataset"></histogram-chart>
                <advanced-stats
                    :team_dataset="team_dataset"
                    :opponent_dataset="opponent_dataset"></advanced-stats>
            </div>
        </div>

    </div>
</template>

<script>

import readXlsxFile  from 'read-excel-file';
import {Chart} from 'highcharts-vue';
import TeamResults from '@/components/TeamResults.vue'
import HistogramChart from '@/components/HistogramChart.vue'
import AdvancedStats from '@/components/AdvancedStats.vue'
import Game from '@/models/Game'

import exporting from "highcharts/modules/exporting"
import Highcharts from "highcharts";

exporting(Highcharts);

export default {
    name: 'Visualizer',

    data: function() {
        return {
            games: [],
            game_attrs: [],
            data_field: null,
            size: 10,
            chart_options: {},
            extra_metric: "xG",
            team_dataset: [],
            opponent_dataset: []
        }
    },
    components: {
        highcharts: Chart,
        TeamResults,
        HistogramChart,
        AdvancedStats
    },

    watch: {
        'games': {
            handler: function() {
                this.redraw();
            },
            deep: true
        }
    },

    methods: {
        async onFileChange(ev) {
            var files = ev.target.files || ev.dataTransfer.files;

            if (files.length != 1) {
                alert("Select exactly one file!");
                return;
            }

            if (files[0].type == "application/json") {
                // fox_cub data detected
                var data = await files[0].text();
                var games = Game.asFoxcub(JSON.parse(data));

                if (games.length < 1) {
                    alert("Games not found!");
                    return;
                }

                this.game_attrs = Object.keys(games[0].team_data);
                this.data_field = this.game_attrs[0];
                this.games = games.sort((a, b) => b.timestamp - a.timestamp);
            } else {
                // try as wyscout data
                readXlsxFile(files[0]).then((rows) => {
                    let raw_fields = rows[0];
                    let import_data = rows.slice(3);
                    var games = Game.asWyscout(raw_fields, import_data);
                    this.game_attrs = Object.keys(games[0].team_data);

                    this.data_field = this.game_attrs[0];
                    this.games = games.sort((a, b) => b.timestamp - a.timestamp);
                })
            }
        },

        redraw() {
            this.chart_options = this.getChartOptions();
        },

        getChartOptions() {
            var selected_games = Array.from(this.games)
                .reverse()
                .filter(g => g.selected);

            var date = selected_games.map(g => new Date(g.timestamp))

            this.team_dataset = this.getFieldArr(selected_games.map(g => g.team_data));
            this.opponent_dataset = this.getFieldArr(selected_games.map(g => g.opponent_data));

            const [team_avg, team_set] = this.getChartData(this.team_dataset);
            const [opponent_avg, opponent_set] = this.getChartData(this.opponent_dataset);

            return {
                title: { text: this.data_field },
                xAxis: {
                    type: 'datetime',
                    categories: date
                },
                series: [{
                    name: `Team (${team_avg})`,
                    data: team_set
                }, {
                    name: `Opponent (${opponent_avg})`,
                    data: opponent_set
                }],

                exporting: {
                    buttons: {
                        contextButton: {
                            menuItems: ['viewFullscreen', 'downloadPDF']
                        }
                    }
                }
            }
        },

        getChartData(points) {
            var point_cluster = points
                .map((v, i) => points.slice(0,i+1)
                .slice(-this.size));

            let arr = point_cluster.map(batch => batch.reduce(
                (a, b) => +a + +b, 0) / batch.length)

            let avg = this.getAvg(points);
            return [avg.toFixed(3), arr];
        },

        getFieldArr(data) {
            return data.map(g => g[this.data_field]);
        },

        getAvg(dataset) {
            return dataset.reduce((pr, cr) => pr + cr) / dataset.length;
        }
    },

}
</script>
