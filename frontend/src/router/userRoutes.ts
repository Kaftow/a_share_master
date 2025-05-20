import type { RouteRecordRaw } from 'vue-router'
import RegisterForm from '@/views/user/RegisterForm.vue'
import LoginForm from '@/views/user/LoginForm.vue'
import ChangePasswordForm from '@/views/user/ChangePasswordForm.vue'
// import DeleteAccountForm from '@/views/user/DeleteAccountForm.vue'

const userRoutes: RouteRecordRaw[] = [
  {
    path: '/register',
    name: 'Register',
    component: RegisterForm,
    meta: { title: '注册', icon: 'User' }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginForm,
    meta: { title: '登录', icon: 'UserFilled' }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePasswordForm,
    meta: { title: '修改密码', icon: 'Lock' }
  },
  // {
  //   path: '/delete-account',
  //   name: 'DeleteAccount',
  //   component: DeleteAccountForm,
  //   meta: { title: '注销账户', icon: 'Delete' }
  // },
]

export default userRoutes

