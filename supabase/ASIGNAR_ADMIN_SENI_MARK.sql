-- SEN$I MARK: asigna tu usuario existente de Authentication.
-- Reemplaza CAMBIA_AQUI_TU_EMAIL por tu correo y ejecuta DESPUES del setup.
DO $$
DECLARE
  v_email text := 'CAMBIA_AQUI_TU_EMAIL';
  v_id uuid;
BEGIN
  IF v_email = 'CAMBIA_AQUI_TU_EMAIL' THEN
    RAISE EXCEPTION 'Reemplaza CAMBIA_AQUI_TU_EMAIL por tu propio correo en Authentication';
  END IF;
  SELECT id INTO v_id FROM auth.users WHERE lower(email) = lower(trim(v_email));
  IF v_id IS NULL THEN
    RAISE EXCEPTION 'El usuario no existe en Authentication > Users';
  END IF;
  INSERT INTO public.license_admins(user_id, role) VALUES (v_id, 'founder')
  ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role;
END $$;
