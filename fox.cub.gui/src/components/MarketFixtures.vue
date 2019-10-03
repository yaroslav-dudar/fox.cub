<template>
    <div class="pure-g">
        <div class="pure-u-1-2">
            <div v-for="day in Object.keys(fixtures)" :key="day">
                <h3>{{day}}</h3>
                <table class="pure-table pure-table-bordered center" style="width:100%;">
                    <thead>
                        <tr>
                            <th>Home Team</th>
                            <th>Away Team</th>
                            <th>Event Date</th>
                            <th>Detail Odds</th>
                        </tr>
                    </thead>
                    <tr v-for="f in fixtures[day]" :key="f._id.$oid">
                        <td>{{f.home_name}}</td>
                        <td>{{f.away_name}}</td>
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
    </div>
</template>

<script>
import router from '@/router'

export default {
    props: ['fixtures'],
    methods: {
        redirectToEvent(fixture) {
            router.push({
                path: 'single_market', query: { fixture: fixture }
            })
        }
    }
}
</script>
