<template>
    <div>
        <table class="pure-table pure-table-bordered center">
            <thead>
                <tr>
                    <th>Home Team</th>
                    <th>Away Team</th>
                    <th>Event Date</th>
                    <th>Detail Odds</th>
                </tr>
            </thead>
            <tr v-for="f in fixtures" :key="f._id.$oid">
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
