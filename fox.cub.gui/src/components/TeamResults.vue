<template>
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Team</th>
                <th>Score</th>
                <th>Away Team</th>
            </tr>
        </thead>
        <tr v-for="g in games" :key="g._id.$oid">
            <td v-if="g.venue == 'home'"><strong>{{g.team[0].name}}</strong></td>
            <td v-else>{{g.opponent[0].name}}</td>

            <td v-if="g.venue == 'home'">{{g.goals_for}} - {{g.goals_against}}</td>
            <td v-else>{{g.goals_against}} - {{g.goals_for}}</td>

            <td v-if="g.venue == 'home'">{{g.opponent[0].name}}</td>
            <td v-else><strong>{{g.team[0].name}}</strong>
            </td>
        </tr>
    </table>
</template>

<script>
export default {
    props: ['games']
}
</script>
