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

        <highcharts :options="chart_options"></highcharts>
    </div>
</template>

<script>

import readXlsxFile  from 'read-excel-file';
import {Chart} from 'highcharts-vue';

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
        }
    },
    components: {
        highcharts: Chart
    },

    watch: {
        'picked_side': {
            handler: function() {
                this.redraw();
            }
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
            })
        },

        redraw() {
            this.chart_options = this.getChartOptions();
        },

        getChartOptions() {
            var team_data = this.import_data
                .filter((r,i) => i % 2 == 0)
                .reverse();

            var opponent_data = this.import_data
                .filter((r,i) => i % 2 == 1)
                .reverse();

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
                }]
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
