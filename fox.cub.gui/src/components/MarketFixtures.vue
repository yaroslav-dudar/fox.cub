<template>
    <div class="pure-g">
        <div class="pure-u-1-2">
            <table class="pure-table pure-table-bordered center" style="width:100%;">
                <thead>
                    <tr>
                        <th>Home Team</th>
                        <th>Away Team</th>
                        <th>Event Date</th>
                        <th>Detail Odds</th>
                    </tr>
                </thead>
                <tr v-for="f in fixtures" :key="f._id.$oid">
                    <fixture-column
                        v-bind:fixture="f"
                        v-bind:venue="Venue.home">
                    </fixture-column>
                    <fixture-column
                        v-bind:fixture="f"
                        v-bind:venue="Venue.away">
                    </fixture-column>
                    <td>{{f.date.$date}}</td>
                    <td>
                        <button v-on:click="redirectToEvent(f._id.$oid)">
                            Go
                        </button>
                    </td>
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
        redirectToEvent(fixture) {
            router.push({
                path: 'single_market', query: { fixture: fixture }
            })
        }
    }
}
</script>
