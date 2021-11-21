<template>
  <v-app>
    <v-content class="grey lighten-4">
      <Navbar/>
      <div class="mx-4 mb-4">
        <keep-alive>
          <router-view></router-view>
        </keep-alive>
      </div>
    </v-content>
  </v-app>
</template>

<script>
import Navbar from '@/components/Navbar'

export default {
  name: 'App',

  components: {
    Navbar
  },

  data: () => ({
    //
  }),
};
</script>

