<template>
    <div>
        <h3>Select file</h3>
        <input type="file" @change="onFileChange">

        <select v-model="data_field" @change="redraw()">
            <option
                v-for="(field, idx) in parsed_fields" :key="field"
                v-bind:value='idx'> {{field}}
            </option>
        </select>
        <hr>

        <div class="pure-g">
            <div class="pure-u-2-5">
                <team-results v-bind:games="results_set"></team-results>
            </div>
            <div class="pure-u-3-5" >
                <highcharts :options="chart_options" style="height: 400px;"></highcharts>
            </div>
        </div>

    </div>
</template>

<script>

import readXlsxFile  from 'read-excel-file';
import {Chart} from 'highcharts-vue';
import TeamResults from '@/components/TeamResults.vue'

import exporting from "highcharts/modules/exporting"
import Highcharts from "highcharts";

exporting(Highcharts);

export default {
    name: 'Visualizer',

    data: function() {
        return {
            import_data: {},
            raw_fields: [],
            parsed_fields: [],
            data_field: -1,
            size: 6,
            chart_options: {},
            results_set: []
        }
    },
    components: {
        highcharts: Chart,
        TeamResults
    },

    watch: {
        'results_set': {
            handler: function() {
                this.redraw();
            },
            deep: true
        }
    },

    methods: {
        onFileChange(ev) {
            var files = ev.target.files || ev.dataTransfer.files;

            if (files.length != 1) {
                alert("Select exactly one file!");
                return;
            }

            readXlsxFile(files[0]).then((rows) => {
                this.raw_fields = rows[0];
                this.import_data = rows.slice(3);

                this.prepareDataFields();
                this.prepareTeamResults();
            })
        },

        redraw() {
            this.chart_options = this.getChartOptions();
        },

        getChartOptions() {
            var team_data = this.import_data
                .filter((_,i) => i % 2 == 0)
                .reverse()
                .filter((_, i) => this.isGameSelected(this.results_set[i]));

            var opponent_data = this.import_data
                .filter((r,i) => i % 2 == 1)
                .reverse()
                .filter((_, i) => this.isGameSelected(this.results_set[i]));

            var date = team_data.map(row => row[0]);

            return {
                title: { text: this.parsed_fields[this.data_field] },
                xAxis: {
                    type: 'datetime',
                    categories: date
                },
                series: [{
                    name: 'Team',
                    data: this.getChartPoints(team_data)
                }, {
                    name: 'Opponent',
                    data: this.getChartPoints(opponent_data)
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

        getChartPoints(data) {
            var points = data.map(row => row[this.data_field]);

            var point_cluster = points
                .map((v, i) => points.slice(0,i+1)
                .slice(-this.size));

            return point_cluster.map(batch => batch.reduce(
                (a, b) => +a + +b, 0) / batch.length)
        },

        prepareTeamResults() {
            var team_data = this.import_data
                .filter((r,i) => i % 2 == 0)
                .reverse();

            var opponent_data = this.import_data
                .filter((r,i) => i % 2 == 1)
                .reverse();

            let goal_field = this.parsed_fields
                .findIndex((f) => f == "Goals");
            let team_field = this.parsed_fields
                .findIndex((f) => f == "Team");

            var res = [];
            let team_name = team_data[0][team_field];

            team_data.forEach((_, i) => {
                res.push({
                    _id: {$oid: i},
                    venue: this.getVenue(team_data[i], team_name),
                    selected: true,
                    goals_for: team_data[i][goal_field],
                    goals_against: opponent_data[i][goal_field],
                    team: [{name: team_name}],
                    opponent: [{name: opponent_data[i][team_field]}]
                })
            });

            this.results_set = res;

        },

        getVenue(row, team) {
            let match_field = this.parsed_fields
                .findIndex((f) => f == "Match");

            return row[match_field].startsWith(team) ? "home": "away";
        },

        isGameSelected(game) {
            return game ? game.selected : true;
        },

        prepareDataFields() {
            this.raw_fields.forEach(field => {
                if (field == null) return;
                var sub_fields = field.split("/");

                if (sub_fields.length == 1)
                    this.parsed_fields.push(sub_fields[0]);
                else if (sub_fields.length == 2) {
                    this.parsed_fields.push(sub_fields[0]);
                    this.parsed_fields.push(`${sub_fields[1]} ${sub_fields[0]}`);
                    this.parsed_fields.push(`${sub_fields[1]} ${sub_fields[0]} %`);
                }
                else if (sub_fields.length == 4) {
                    this.parsed_fields.push(sub_fields[0]);
                    this.parsed_fields.push(`${sub_fields[1]} ${sub_fields[0]}`);
                    this.parsed_fields.push(`${sub_fields[2]} ${sub_fields[0]}`);
                    this.parsed_fields.push(`${sub_fields[3]} ${sub_fields[0]}`);
                }
            });
        }
    },

}
</script>
