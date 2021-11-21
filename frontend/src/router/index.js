import Vue from 'vue'
import VueRouter from 'vue-router'
import GPUOverview from '../views/GPUOverview.vue'
import Processes from '../views/Processes.vue'
import Users from '../views/Users.vue'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'GPUOverview',
        component: GPUOverview
    },
    {
        path: '/processes',
        name: 'Processes',
        component: Processes
    },
    {
        path: '/users',
        name: 'Users',
        component: Users
    }
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

export default router

