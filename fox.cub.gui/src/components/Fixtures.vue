<template>
    <div class="pure-g">
        <div v-for="day in Object.keys(fixtures)" :key="day" class="pure-u-1-1">
            <h3>{{day}}</h3>
            <table class="pure-table pure-table-bordered center" style="width:70%;">
                <thead>
                    <tr>
                        <th>Home Team</th>
                        <th>Away Team</th>
                        <th>Event Date</th>
                        <th>Weather Forecast</th>
                        <th>Detail Stats</th>
                    </tr>
                </thead>
                <tr v-for="f in fixtures[day]" :key="f._id.$oid">
                    <fixture-column
                        v-bind:fixture="f"
                        v-bind:venue="Venue.home">
                    </fixture-column>
                    <fixture-column
                        v-bind:fixture="f"
                        v-bind:venue="Venue.away">
                    </fixture-column>
                    <td>{{f.date.$date}}</td>
                    <td>No data</td>
                    <td v-if="f.home_id && f.away_id"><button
                        v-on:click="redirectToGame(f._id.$oid)">
                    Get Stats</button></td>
                    <td v-else>Teams Not available</td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script>
import router from '@/router';
import FixtureColumn from '@/components/FixtureColumn.vue';
import {Venue} from '@/models/Game';

export default {
    props: ['fixtures'],
    data() {
        return {
            Venue
        }
    },
    components: {
        FixtureColumn
    },
    methods: {
        redirectToGame(fixture) {
            router.push({
                path: 'game', query: { fixture: fixture }
            })
        },

        getClass(value) {
            if (!value) return "freeze";
            if (value > 1.02) return "up";
            if (value < 0.98) return "down";
            return "freeze";
        },

        toFixed(value) {
            if (!value) return 1.0;
            return value.toFixed(2);
        }
    }
}
</script>
