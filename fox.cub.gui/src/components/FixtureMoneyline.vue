<template>
    <span v-if="fixture.homeWin">
        {{fixture.homeWin}} / {{fixture.draw}} / {{fixture.awayWin}}
    </span>
    <span  v-else> No data </span>
</template>

<script>

export default {
    props: ['fixture']
}
</script>
