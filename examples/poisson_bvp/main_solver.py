exec(open("./imports.py").read())

print("")
print("*************************")
print("* Setting up...")
print("*************************")

exec(open("./configs.py").read())
exec(open(source_type).read())
print("Multipole order =", m_order)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)
exec(open("./make_mesh.py").read())

print("Bounding box: [", a, b, "]^2")
print("Number of boundary nodes: ", bdry_discr.nnodes)

print("")
print("*************************")
print("* Evaluating: ")
print("* Volume Potential... ")
print("*************************")

from volumential.volume_fmm import drive_volume_fmm
pot, = drive_volume_fmm(trav, wrangler, source_vals * q_weights, source_vals)

# interpolate solution
from volumential.volume_fmm import interpolate_volume_potential

nodes_x = vol_discr.nodes()[0].with_queue(queue).get()
nodes_y = vol_discr.nodes()[1].with_queue(queue).get()
nodes = make_obj_array( # get() first for CL compatibility issues
        [cl.array.to_device(queue, nodes_x),
         cl.array.to_device(queue, nodes_y)])
vol_pot = interpolate_volume_potential(nodes,
        trav, wrangler, pot)
print("Done.")

print("")
print("*************************")
print("* Evaluating: ")
print("* Boundary Conditions... ")
print("*************************")

exec(open("./prepare_bc.py").read())
print("Done.")

print("")
print("*************************")
print("* Solving BVP... ")
print("*************************")

exec(open("./solve_bvp.py").read())

print("")
print("*************************")
print("* Finalizing Solution... ")
print("*************************")

exec(open("./finalize_solu.py").read())
print("Done.")

print("")
print("*************************")
print("* Postprocessing... ")
print("*************************")

poisson_true_sol = cl.array.to_device(queue,
        exact_solu(nodes_x, nodes_y))
poisson_err = solu - poisson_true_sol

rel_err = (
        norm(vol_discr, queue, poisson_err)
        /
        norm(vol_discr, queue, poisson_true_sol))
print("rel err: %g" % rel_err)

exec(open("./postprocess.py").read())
