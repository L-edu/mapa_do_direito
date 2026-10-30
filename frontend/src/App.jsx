import { Route, Routes } from 'react-router-dom';
import Layout from './components/layout/Layout.jsx';
import RotaProtegida from './components/layout/RotaProtegida.jsx';
import Inicio from './pages/Inicio.jsx';
import Simulador from './pages/Simulador.jsx';
import Login from './pages/Login.jsx';
import Registro from './pages/Registro.jsx';
import Programas from './pages/Programas.jsx';
import ProgramaDetalhe from './pages/ProgramaDetalhe.jsx';
import ProgramaForm from './pages/ProgramaForm.jsx';
import Familias from './pages/Familias.jsx';
import FamiliaForm from './pages/FamiliaForm.jsx';
import FamiliaDetalhe from './pages/FamiliaDetalhe.jsx';
import SimulacaoDetalhe from './pages/SimulacaoDetalhe.jsx';
import Painel from './pages/admin/Painel.jsx';
import Parametros from './pages/admin/Parametros.jsx';
import Usuarios from './pages/admin/Usuarios.jsx';
import NaoEncontrado from './pages/NaoEncontrado.jsx';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Públicas */}
        <Route path="/" element={<Inicio />} />
        <Route path="/simulador" element={<Simulador />} />
        <Route path="/programas" element={<Programas />} />
        <Route path="/programas/:id" element={<ProgramaDetalhe />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />

        {/* Exigem login (qualquer papel) */}
        <Route element={<RotaProtegida />}>
          <Route path="/familias" element={<Familias />} />
          <Route path="/familias/nova" element={<FamiliaForm />} />
          <Route path="/familias/:id" element={<FamiliaDetalhe />} />
          <Route path="/familias/:id/editar" element={<FamiliaForm />} />
          <Route path="/simulacoes/:id" element={<SimulacaoDetalhe />} />
        </Route>

        {/* Somente administrador */}
        <Route element={<RotaProtegida papeis={['admin']} />}>
          <Route path="/admin" element={<Painel />} />
          <Route path="/admin/parametros" element={<Parametros />} />
          <Route path="/admin/usuarios" element={<Usuarios />} />
          <Route path="/admin/programas/novo" element={<ProgramaForm />} />
          <Route path="/admin/programas/:id/editar" element={<ProgramaForm />} />
        </Route>

        <Route path="*" element={<NaoEncontrado />} />
      </Route>
    </Routes>
  );
}
