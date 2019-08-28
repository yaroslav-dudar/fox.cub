<style>
    tr.win {
        background-color: #90EE90;
    }

    tr.draw {
        background-color: #C0C0C0;
    }

    tr.lose {
        background-color: #F08080;
    }

    tr.unselected {
        opacity: 0.4;
    }
</style>
<template>
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Selected</th>
                <th>Home Team</th>
                <th>Score</th>
                <th>Away Team</th>
            </tr>
        </thead>
        <tr v-for="g in games"
            :key="g._id.$oid"
            v-bind:class="[getResult(g.goals_for, g.goals_against), isSelected(g)]">

            <td>
                <input type="checkbox" v-model="g.selected">
            </td>
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
    props: ['games'],
    methods: {
        getResult(goals_for, goals_against) {
            if (goals_for > goals_against) {
                return 'win';
            } else if (goals_for == goals_against) {
                return 'draw';
            } else {
                return 'lose';
            }
        },
        isSelected(game) {
            return game.selected ? '' : 'unselected';
        }
    }
}
</script>
